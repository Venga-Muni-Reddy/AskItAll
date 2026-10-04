import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.db.models.identity import User
from app.db.models.conversation import Conversation, Message, MessageCitation
from app.services.retrieval.hybrid import HybridRetriever
from app.services.ai_gateway.base import AIGateway
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    CitationItem,
    ChatUsage,
    ChatMetadata,
)

router = APIRouter()


@router.post("", response_model=ChatResponse)
async def chat_message(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # 1. Resolve or create conversation
    conv_id = payload.conversation_id
    if not conv_id:
        new_conv = Conversation(
            workspace_id=payload.scope.workspace_id,
            user_id=current_user.id,
            title=payload.message[:50] + ("..." if len(payload.message) > 50 else ""),
            status="active",
        )
        db.add(new_conv)
        await db.flush()
        conv_id = new_conv.id
    else:
        conv_query = select(Conversation).where(Conversation.id == conv_id)
        conv_res = await db.execute(conv_query)
        if not conv_res.scalar_one_or_none():
            conv_id = uuid.uuid4()
            new_conv = Conversation(
                id=conv_id,
                workspace_id=payload.scope.workspace_id,
                user_id=current_user.id,
                title=payload.message[:50],
            )
            db.add(new_conv)
            await db.flush()

    # 2. Record User Message
    user_msg = Message(
        conversation_id=conv_id,
        sender_type="user",
        content=payload.message,
        token_count=len(payload.message.split()),
        metadata_json={},
    )
    db.add(user_msg)
    await db.flush()

    # 3. Retrieve relevant knowledge evidence
    candidates = await HybridRetriever.retrieve(
        db=db,
        workspace_id=payload.scope.workspace_id,
        query=payload.message,
        knowledge_base_ids=payload.scope.knowledge_base_ids,
        top_k=5,
    )

    # 4. Zero-Hallucination & Insufficient Evidence Check
    if not candidates:
        no_evidence_answer = (
            "I couldn't find sufficient information in the connected knowledge to answer this question."
        )
        bot_msg = Message(
            conversation_id=conv_id,
            sender_type="assistant",
            content=no_evidence_answer,
            token_count=len(no_evidence_answer.split()),
            metadata_json={"insufficient_evidence": True},
        )
        db.add(bot_msg)
        await db.commit()
        await db.refresh(bot_msg)

        return ChatResponse(
            conversation_id=conv_id,
            message_id=bot_msg.id,
            answer=no_evidence_answer,
            citations=[],
            usage=ChatUsage(input_tokens=10, output_tokens=15, total_tokens=25),
            metadata=ChatMetadata(
                model="deterministic-guardrail",
                retrieval_strategy=["dense", "sparse"],
            ),
        )

    # 5. Build Grounded Context Prompt
    context_blocks = []
    citations_data = []

    for idx, item in enumerate(candidates, 1):
        chunk = item["chunk"]
        doc_title = item.get("document_title", "Document")
        snippet = chunk.content.strip()
        context_blocks.append(f"[{idx}] (Source: {doc_title}, Page: {chunk.page_number or 'N/A'})\n{snippet}")

        citations_data.append(
            {
                "chunk_id": chunk.id,
                "document_id": chunk.document_id,
                "document_title": doc_title,
                "version_id": chunk.version_id,
                "page": chunk.page_number,
                "section": chunk.section_title,
                "quote": snippet[:200] + "..." if len(snippet) > 200 else snippet,
            }
        )

    system_prompt = (
        "You are AskItAll, an enterprise AI assistant strictly grounded in authorized organizational knowledge.\n"
        "Rules:\n"
        "1. Answer ONLY using the provided evidence context below.\n"
        "2. If the context does not contain enough evidence, explicitly state that you cannot answer.\n"
        "3. Preserve facts, numbers, dates, and relationships accurately.\n"
        "4. Include inline citations like [1], [2] referencing the source chunks."
    )

    user_prompt = f"Evidence Context:\n\n{chr(10).join(context_blocks)}\n\nUser Question: {payload.message}\n\nPlease provide a clear, factual answer with source citations."

    ai_result = await AIGateway.generate_chat_response(
        prompt=user_prompt,
        system_instruction=system_prompt,
    )

    answer_text = ai_result["text"]

    # 6. Save Assistant Message and Citations
    bot_msg = Message(
        conversation_id=conv_id,
        sender_type="assistant",
        content=answer_text,
        token_count=ai_result.get("output_tokens", 0),
        metadata_json={"model": ai_result["model"]},
    )
    db.add(bot_msg)
    await db.flush()

    citation_responses = []
    for c in citations_data:
        msg_citation = MessageCitation(
            message_id=bot_msg.id,
            chunk_id=c["chunk_id"],
            document_id=c["document_id"],
            version_id=c["version_id"],
            page_number=c["page"],
            section_title=c["section"],
            quote=c["quote"],
        )
        db.add(msg_citation)
        await db.flush()

        citation_responses.append(
            CitationItem(
                id=msg_citation.id,
                document_id=c["document_id"],
                document_title=c["document_title"],
                version_id=c["version_id"],
                type="paragraph",
                page=c["page"],
                section=c["section"],
                quote=c["quote"],
            )
        )

    await db.commit()
    await db.refresh(bot_msg)

    return ChatResponse(
        conversation_id=conv_id,
        message_id=bot_msg.id,
        answer=answer_text,
        citations=citation_responses,
        usage=ChatUsage(
            input_tokens=ai_result.get("input_tokens", 0),
            output_tokens=ai_result.get("output_tokens", 0),
            total_tokens=ai_result.get("input_tokens", 0) + ai_result.get("output_tokens", 0),
        ),
        metadata=ChatMetadata(
            model=ai_result.get("model", "default"),
            retrieval_strategy=["dense", "sparse"],
        ),
    )
