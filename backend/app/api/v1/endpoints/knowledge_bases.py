import uuid
import re
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.exceptions import NotFoundException, ForbiddenException
from app.db.session import get_db
from app.db.models.identity import User
from app.db.models.organization import WorkspaceMembership
from app.db.models.knowledge import KnowledgeBase
from app.schemas.knowledge_base import KnowledgeBaseCreate, KnowledgeBaseUpdate, KnowledgeBaseResponse

router = APIRouter()


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-")


@router.get("/workspaces/{workspace_id}/knowledge-bases", response_model=List[KnowledgeBaseResponse])
async def list_knowledge_bases(
    workspace_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify user is member of workspace
    membership = await db.execute(
        select(WorkspaceMembership).where(
            WorkspaceMembership.workspace_id == workspace_id,
            WorkspaceMembership.user_id == current_user.id,
        )
    )
    if not membership.scalar_one_or_none():
        raise ForbiddenException("Access to workspace denied.")

    query = select(KnowledgeBase).where(KnowledgeBase.workspace_id == workspace_id)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/workspaces/{workspace_id}/knowledge-bases", response_model=KnowledgeBaseResponse, status_code=status.HTTP_201_CREATED)
async def create_knowledge_base(
    workspace_id: uuid.UUID,
    payload: KnowledgeBaseCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    membership = await db.execute(
        select(WorkspaceMembership).where(
            WorkspaceMembership.workspace_id == workspace_id,
            WorkspaceMembership.user_id == current_user.id,
        )
    )
    if not membership.scalar_one_or_none():
        raise ForbiddenException("Access to workspace denied.")

    slug = payload.slug or slugify(payload.name)
    existing = await db.execute(
        select(KnowledgeBase).where(
            KnowledgeBase.workspace_id == workspace_id,
            KnowledgeBase.slug == slug,
        )
    )
    if existing.scalar_one_or_none():
        slug = f"{slug}-{uuid.uuid4().hex[:6]}"

    kb = KnowledgeBase(
        workspace_id=workspace_id,
        name=payload.name,
        slug=slug,
        description=payload.description,
        is_public=payload.is_public,
        status="active",
    )
    db.add(kb)
    await db.commit()
    await db.refresh(kb)
    return kb


@router.get("/knowledge-bases/{id}", response_model=KnowledgeBaseResponse)
async def get_knowledge_base(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(KnowledgeBase).where(KnowledgeBase.id == id)
    result = await db.execute(query)
    kb = result.scalar_one_or_none()
    if not kb:
        raise NotFoundException("Knowledge Base not found.")
    return kb
