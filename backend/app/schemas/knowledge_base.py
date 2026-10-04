import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class KnowledgeBaseCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    slug: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    is_public: bool = False


class KnowledgeBaseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None


class KnowledgeBaseResponse(BaseModel):
    id: uuid.UUID
    workspace_id: uuid.UUID
    name: str
    slug: str
    description: Optional[str] = None
    is_public: bool
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
