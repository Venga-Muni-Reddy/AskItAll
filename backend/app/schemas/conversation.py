import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from app.schemas.chat import CitationItem


class ConversationCreate(BaseModel):
    workspace_id: uuid.UUID
    title: Optional[str] = "New Conversation"
    knowledge_base_ids: List[uuid.UUID] = []


class ConversationResponse(BaseModel):
    id: uuid.UUID
    workspace_id: uuid.UUID
    user_id: uuid.UUID
    title: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    id: uuid.UUID
    conversation_id: uuid.UUID
    sender_type: str  # user, assistant
    content: str
    token_count: int
    citations: List[CitationItem] = []
    created_at: datetime

    class Config:
        from_attributes = True
