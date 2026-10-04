import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class WorkspaceCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    slug: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None


class WorkspaceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class WorkspaceResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    slug: str
    description: Optional[str] = None
    status: str
    user_role: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class WorkspaceMemberAdd(BaseModel):
    email: Optional[EmailStr] = None
    user_id: Optional[uuid.UUID] = None
    role: str = Field("member", pattern="^(admin|member|viewer)$")


class WorkspaceMemberUpdate(BaseModel):
    role: str = Field(..., pattern="^(admin|member|viewer)$")


class WorkspaceMemberWithUser(BaseModel):
    membership_id: uuid.UUID
    workspace_id: uuid.UUID
    user_id: uuid.UUID
    email: str
    display_name: str
    role: str
    joined_at: datetime
