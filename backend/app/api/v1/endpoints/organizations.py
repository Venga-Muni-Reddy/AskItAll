import uuid
import re
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.exceptions import NotFoundException, ConflictException
from app.db.session import get_db
from app.db.models.identity import User
from app.db.models.organization import Organization, Membership
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse,
)

router = APIRouter()


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-")


@router.get("", response_model=List[OrganizationResponse])
async def list_organizations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(Organization)
        .join(Membership, Membership.organization_id == Organization.id)
        .where(Membership.user_id == current_user.id)
    )
    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    payload: OrganizationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    slug = payload.slug or slugify(payload.name)
    # Check uniqueness
    existing = await db.execute(select(Organization).where(Organization.slug == slug))
    if existing.scalar_one_or_none():
        slug = f"{slug}-{uuid.uuid4().hex[:6]}"

    org = Organization(
        name=payload.name,
        slug=slug,
        status="active",
    )
    db.add(org)
    await db.flush()

    # Add creator as owner membership
    membership = Membership(
        organization_id=org.id,
        user_id=current_user.id,
        role_name="owner",
        status="active",
    )
    db.add(membership)
    await db.commit()
    await db.refresh(org)
    return org


@router.get("/{id}", response_model=OrganizationResponse)
async def get_organization(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(Organization)
        .join(Membership, Membership.organization_id == Organization.id)
        .where(Organization.id == id, Membership.user_id == current_user.id)
    )
    result = await db.execute(query)
    org = result.scalar_one_or_none()
    if not org:
        raise NotFoundException("Organization not found or you lack permission.")
    return org
