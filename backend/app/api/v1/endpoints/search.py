import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.db.models.identity import User
from app.services.retrieval.hybrid import HybridRetriever
from app.schemas.search import (
    SearchRequest,
    SearchResponse,
    SearchResultItem,
    CitationDetail,
    RetrievalMetadata,
)

router = APIRouter()


@router.post("", response_model=SearchResponse)
async def search_knowledge(
    payload: SearchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    candidates = await HybridRetriever.retrieve(
        db=db,
        workspace_id=payload.scope.workspace_id,
        query=payload.query,
        knowledge_base_ids=payload.scope.knowledge_base_ids,
        top_k=payload.top_k,
    )

    results: list[SearchResultItem] = []
    strategies_used = set()

    for item in candidates:
        chunk = item["chunk"]
        for s in item["sources"]:
            strategies_used.add(s)

        results.append(
            SearchResultItem(
                chunk_id=chunk.id,
                document_id=chunk.document_id,
                version_id=chunk.version_id,
                score=round(item["score"], 4),
                rerank_score=round(item["score"], 4),
                content=chunk.content,
                citation=CitationDetail(
                    type=chunk.chunk_type,
                    document_id=chunk.document_id,
                    document_title=item.get("document_title"),
                    version_id=chunk.version_id,
                    page=chunk.page_number,
                    section=chunk.section_title,
                    quote=chunk.content[:150] + "..." if len(chunk.content) > 150 else chunk.content,
                ),
            )
        )

    return SearchResponse(
        query=payload.query,
        results=results,
        retrieval=RetrievalMetadata(
            strategy=list(strategies_used) if strategies_used else ["dense", "sparse"],
            candidate_count=len(results),
            returned_count=len(results),
        ),
    )
