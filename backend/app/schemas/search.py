import uuid
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class SearchScope(BaseModel):
    workspace_id: uuid.UUID
    knowledge_base_ids: List[uuid.UUID] = []


class SearchFilters(BaseModel):
    document_types: Optional[List[str]] = None
    created_after: Optional[str] = None


class SearchRequest(BaseModel):
    query: str
    scope: SearchScope
    filters: Optional[SearchFilters] = None
    top_k: int = 10
    response_detail: str = "standard"


class CitationDetail(BaseModel):
    type: str = "paragraph"
    document_id: uuid.UUID
    document_title: Optional[str] = None
    version_id: Optional[uuid.UUID] = None
    page: Optional[int] = None
    section: Optional[str] = None
    quote: Optional[str] = None


class SearchResultItem(BaseModel):
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    version_id: uuid.UUID
    score: float
    rerank_score: Optional[float] = None
    content: str
    citation: CitationDetail


class RetrievalMetadata(BaseModel):
    strategy: List[str]
    candidate_count: int
    returned_count: int


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResultItem]
    retrieval: RetrievalMetadata
