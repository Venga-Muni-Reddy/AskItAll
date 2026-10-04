import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user
from app.core.exceptions import NotFoundException, ForbiddenException
from app.db.session import get_db
from app.db.models.identity import User
from app.db.models.conversation import Conversation, ConversationScope, Message, MessageCitation
from app.schemas.conversation import ConversationCreate, ConversationResponse, MessageResponse
from app.schemas.chat import CitationItem

router = APIRouter()


@router.get("", response_model=List[ConversationResponse])
async def list_conversations(
    workspace_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(Conversation)
        .where(Conversation.workspace_id == workspace_id, Conversation.user_id == current_user.id)
        .order_by(Conversation.updated_at.desc())
    )
    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    payload: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    conv = Conversation(
        workspace_id=payload.workspace_id,
        user_id=current_user.id,
        title=payload.title or "New Conversation",
        status="active",
    )
    db.add(conv)
    await db.flush()

    for kb_id in payload.knowledge_base_ids:
        scope = ConversationScope(
            conversation_id=conv.id,
            knowledge_base_id=kb_id,
        )
        db.add(scope)

    await db.commit()
    await db.refresh(conv)
    return conv


@router.get("/{id}", response_model=ConversationResponse)
async def get_conversation(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Conversation).where(Conversation.id == id, Conversation.user_id == current_user.id)
    result = await db.execute(query)
    conv = result.scalar_one_or_none()
    if not conv:
        raise NotFoundException("Conversation not found.")
    return conv


@router.get("/{id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    conv_query = select(Conversation).where(Conversation.id == id, Conversation.user_id == current_user.id)
    conv = (await db.execute(conv_query)).scalar_one_or_none()
    if not conv:
        raise NotFoundException("Conversation not found.")

    query = (
        select(Message)
        .options(selectinload(Message.citations))
        .where(Message.conversation_id == id)
        .order_by(Message.created_at.asc())
    )
    result = await db.execute(query)
    messages = result.scalars().all()

    response_list = []
    for msg in messages:
        citations = [
            CitationItem(
                id=c.id,
                document_id=c.document_id,
                version_id=c.version_id,
                type="paragraph",
                page=c.page_number,
                section=c.section_title,
                quote=c.quote,
            )
            for c in msg.citations
        ]
        response_list.append(
            MessageResponse(
                id=msg.id,
                conversation_id=msg.conversation_id,
                sender_type=msg.sender_type,
                content=msg.content,
                token_count=msg.token_count,
                citations=citations,
                created_at=msg.created_at,
            )
        )
    return response_list
