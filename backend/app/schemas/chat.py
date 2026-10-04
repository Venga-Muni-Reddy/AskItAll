import uuid
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ChatScope(BaseModel):
    workspace_id: uuid.UUID
    knowledge_base_ids: List[uuid.UUID] = []


class ChatRequest(BaseModel):
    conversation_id: Optional[uuid.UUID] = None
    message: str
    scope: ChatScope
    response_mode: str = "complete"  # complete | stream


class CitationItem(BaseModel):
    id: uuid.UUID
    document_id: uuid.UUID
    document_title: Optional[str] = None
    version_id: Optional[uuid.UUID] = None
    type: str = "paragraph"
    page: Optional[int] = None
    section: Optional[str] = None
    quote: Optional[str] = None


class ChatUsage(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0


class ChatMetadata(BaseModel):
    model: str
    retrieval_strategy: List[str]


class ChatResponse(BaseModel):
    conversation_id: uuid.UUID
    message_id: uuid.UUID
    answer: str
    citations: List[CitationItem] = []
    usage: ChatUsage = Field(default_factory=ChatUsage)
    metadata: ChatMetadata
