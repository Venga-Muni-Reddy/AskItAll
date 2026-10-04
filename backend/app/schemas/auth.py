import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    display_name: str = Field(..., min_length=2, max_length=255)
    organization_name: Optional[str] = Field(None, min_length=2, max_length=255)


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenRefreshRequest(BaseModel):
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    display_name: str
    avatar_url: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Optional[UserResponse] = None


class UserOrgSummary(BaseModel):
    organization_id: uuid.UUID
    name: str
    slug: str
    role: str


class UserWorkspaceSummary(BaseModel):
    workspace_id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    slug: str
    role: str


class UserMeResponse(BaseModel):
    user: UserResponse
    organizations: List[UserOrgSummary] = []
    workspaces: List[UserWorkspaceSummary] = []
