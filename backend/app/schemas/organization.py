import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


class OrganizationCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    slug: Optional[str] = Field(None, max_length=100)


class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None


class OrganizationResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    status: str
    user_role: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class MembershipResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    user_id: uuid.UUID
    role_name: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class OrganizationMemberAdd(BaseModel):
    email: EmailStr
    role_name: str = Field("member", pattern="^(owner|admin|member|viewer)$")


class OrganizationMemberUpdate(BaseModel):
    role_name: str = Field(..., pattern="^(owner|admin|member|viewer)$")


class OrganizationMemberWithUser(BaseModel):
    membership_id: uuid.UUID
    user_id: uuid.UUID
    email: str
    display_name: str
    role_name: str
    status: str
    joined_at: datetime
