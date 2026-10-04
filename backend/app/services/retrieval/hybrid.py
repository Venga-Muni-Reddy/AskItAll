import uuid
from typing import List, Dict, Any, Optional
from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.knowledge import (
    Chunk,
    ChunkEmbedding,
    Document,
    KnowledgeBaseDocument,
)
from app.services.ai_gateway.base import AIGateway


class HybridRetriever:
    @classmethod
    async def retrieve(
        cls,
        db: AsyncSession,
        workspace_id: uuid.UUID,
        query: str,
        knowledge_base_ids: Optional[List[uuid.UUID]] = None,
        top_k: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Executes hybrid retrieval:
        1. Dense Vector Search via pgvector
        2. Sparse Keyword Search via ILIKE / Full-text
        3. Reciprocal fusion & deduplication
        """
        query_vector = await AIGateway.generate_embedding(query)

        # Base filter: workspace_id and not deleted
        kb_doc_filter = True
        if knowledge_base_ids:
            kb_doc_query = select(KnowledgeBaseDocument.document_id).where(
                KnowledgeBaseDocument.knowledge_base_id.in_(knowledge_base_ids)
            )
            kb_doc_filter = Chunk.document_id.in_(kb_doc_query)

        # 1. Vector Search Query
        vector_query = (
            select(
                Chunk,
                Document.title.label("document_title"),
                (1 - ChunkEmbedding.embedding.cosine_distance(query_vector)).label("similarity_score"),
            )
            .join(ChunkEmbedding, ChunkEmbedding.chunk_id == Chunk.id)
            .join(Document, Document.id == Chunk.document_id)
            .where(
                Chunk.workspace_id == workspace_id,
                Document.deleted_at.is_(None),
                kb_doc_filter,
            )
            .order_by(ChunkEmbedding.embedding.cosine_distance(query_vector))
            .limit(top_k * 2)
        )

        try:
            vector_res = await db.execute(vector_query)
            vector_rows = vector_res.all()
        except Exception:
            vector_rows = []

        # 2. Keyword Search Query
        terms = [t.strip() for t in query.split() if len(t.strip()) > 3]
        keyword_clauses = [Chunk.content.ilike(f"%{t}%") for t in terms[:5]]
        if not keyword_clauses:
            keyword_clauses = [Chunk.content.ilike(f"%{query}%")]

        keyword_query = (
            select(
                Chunk,
                Document.title.label("document_title"),
            )
            .join(Document, Document.id == Chunk.document_id)
            .where(
                Chunk.workspace_id == workspace_id,
                Document.deleted_at.is_(None),
                kb_doc_filter,
                or_(*keyword_clauses),
            )
            .limit(top_k * 2)
        )

        keyword_res = await db.execute(keyword_query)
        keyword_rows = keyword_res.all()

        # 3. Reciprocal Rank Fusion / Scoring Merge
        scores: Dict[uuid.UUID, Dict[str, Any]] = {}

        for rank, row in enumerate(vector_rows):
            chunk = row[0]
            title = row[1]
            sim_score = float(row[2])
            scores[chunk.id] = {
                "chunk": chunk,
                "document_title": title,
                "score": sim_score,
                "sources": ["dense"],
            }

        for rank, row in enumerate(keyword_rows):
            chunk = row[0]
            title = row[1]
            if chunk.id in scores:
                scores[chunk.id]["score"] += 0.2
                scores[chunk.id]["sources"].append("sparse")
            else:
                scores[chunk.id] = {
                    "chunk": chunk,
                    "document_title": title,
                    "score": 0.5,
                    "sources": ["sparse"],
                }

        sorted_candidates = sorted(scores.values(), key=lambda x: x["score"], reverse=True)
        return sorted_candidates[:top_k]
