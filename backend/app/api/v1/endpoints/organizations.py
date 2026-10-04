import uuid
import re
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_organization_role
from app.core.exceptions import NotFoundException, ConflictException, ForbiddenException, AppException
from app.db.session import get_db
from app.db.models.identity import User
from app.db.models.organization import Organization, Membership
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse,
    OrganizationMemberAdd,
    OrganizationMemberUpdate,
    OrganizationMemberWithUser,
)

router = APIRouter()


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-") or "org"


@router.get("", response_model=List[OrganizationResponse])
async def list_organizations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(Organization, Membership.role_name)
        .join(Membership, Membership.organization_id == Organization.id)
        .where(Membership.user_id == current_user.id, Membership.status == "active")
        .order_by(Organization.created_at.desc())
    )
    result = await db.execute(query)
    rows = result.all()
    return [
        OrganizationResponse(
            id=org.id,
            name=org.name,
            slug=org.slug,
            status=org.status,
            user_role=role,
            created_at=org.created_at,
        )
        for org, role in rows
    ]


@router.post("", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    payload: OrganizationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    slug = payload.slug or slugify(payload.name)
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

    membership = Membership(
        organization_id=org.id,
        user_id=current_user.id,
        role_name="owner",
        status="active",
    )
    db.add(membership)
    await db.commit()
    await db.refresh(org)

    return OrganizationResponse(
        id=org.id,
        name=org.name,
        slug=org.slug,
        status=org.status,
        user_role="owner",
        created_at=org.created_at,
    )


@router.get("/{id}", response_model=OrganizationResponse)
async def get_organization(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(Organization, Membership.role_name)
        .join(Membership, Membership.organization_id == Organization.id)
        .where(Organization.id == id, Membership.user_id == current_user.id, Membership.status == "active")
    )
    result = await db.execute(query)
    row = result.first()
    if not row:
        raise NotFoundException("Organization not found or you lack permission.")
    org, role = row
    return OrganizationResponse(
        id=org.id,
        name=org.name,
        slug=org.slug,
        status=org.status,
        user_role=role,
        created_at=org.created_at,
    )


@router.patch("/{id}", response_model=OrganizationResponse)
async def update_organization(
    id: uuid.UUID,
    payload: OrganizationUpdate,
    _membership: Membership = Depends(require_organization_role(["owner", "admin"])),
    db: AsyncSession = Depends(get_db),
):
    org = await db.get(Organization, id)
    if not org:
        raise NotFoundException("Organization not found.")

    if payload.name:
        org.name = payload.name
    if payload.slug:
        org.slug = slugify(payload.slug)

    await db.commit()
    await db.refresh(org)
    return OrganizationResponse(
        id=org.id,
        name=org.name,
        slug=org.slug,
        status=org.status,
        user_role=_membership.role_name,
        created_at=org.created_at,
    )


@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_organization(
    id: uuid.UUID,
    _membership: Membership = Depends(require_organization_role(["owner"])),
    db: AsyncSession = Depends(get_db),
):
    org = await db.get(Organization, id)
    if not org:
        raise NotFoundException("Organization not found.")
    org.status = "deleted"
    await db.commit()
    return {"message": "Organization deactivated successfully."}


@router.get("/{id}/members", response_model=List[OrganizationMemberWithUser])
async def list_organization_members(
    id: uuid.UUID,
    _membership: Membership = Depends(require_organization_role(["owner", "admin", "member"])),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(Membership, User)
        .join(User, User.id == Membership.user_id)
        .where(Membership.organization_id == id)
        .order_by(Membership.created_at.asc())
    )
    result = await db.execute(query)
    rows = result.all()

    return [
        OrganizationMemberWithUser(
            membership_id=m.id,
            user_id=u.id,
            email=u.email,
            display_name=u.display_name,
            role_name=m.role_name,
            status=m.status,
            joined_at=m.created_at,
        )
        for m, u in rows
    ]


@router.post("/{id}/members", response_model=OrganizationMemberWithUser, status_code=status.HTTP_201_CREATED)
async def add_organization_member(
    id: uuid.UUID,
    payload: OrganizationMemberAdd,
    _membership: Membership = Depends(require_organization_role(["owner", "admin"])),
    db: AsyncSession = Depends(get_db),
):
    user_query = select(User).where(User.email == payload.email)
    user = (await db.execute(user_query)).scalar_one_or_none()
    if not user:
        raise NotFoundException(f"User with email '{payload.email}' does not exist.")

    # Check if already a member
    existing = await db.execute(
        select(Membership).where(Membership.organization_id == id, Membership.user_id == user.id)
    )
    if existing.scalar_one_or_none():
        raise ConflictException("User is already a member of this organization.")

    new_member = Membership(
        organization_id=id,
        user_id=user.id,
        role_name=payload.role_name,
        status="active",
    )
    db.add(new_member)
    await db.commit()
    await db.refresh(new_member)

    return OrganizationMemberWithUser(
        membership_id=new_member.id,
        user_id=user.id,
        email=user.email,
        display_name=user.display_name,
        role_name=new_member.role_name,
        status=new_member.status,
        joined_at=new_member.created_at,
    )


@router.patch("/{id}/members/{user_id}", response_model=OrganizationMemberWithUser)
async def update_organization_member_role(
    id: uuid.UUID,
    user_id: uuid.UUID,
    payload: OrganizationMemberUpdate,
    _membership: Membership = Depends(require_organization_role(["owner", "admin"])),
    db: AsyncSession = Depends(get_db),
):
    query = select(Membership, User).join(User, User.id == Membership.user_id).where(
        Membership.organization_id == id,
        Membership.user_id == user_id,
    )
    row = (await db.execute(query)).first()
    if not row:
        raise NotFoundException("Organization member not found.")
    m, u = row

    if m.role_name == "owner" and payload.role_name != "owner":
        # Check if there are other owners
        owner_count = await db.execute(
            select(Membership).where(Membership.organization_id == id, Membership.role_name == "owner")
        )
        if len(owner_count.scalars().all()) <= 1:
            raise AppException("FORBIDDEN", "Cannot demote the sole organization owner.")

    m.role_name = payload.role_name
    await db.commit()

    return OrganizationMemberWithUser(
        membership_id=m.id,
        user_id=u.id,
        email=u.email,
        display_name=u.display_name,
        role_name=m.role_name,
        status=m.status,
        joined_at=m.created_at,
    )


@router.delete("/{id}/members/{user_id}", status_code=status.HTTP_200_OK)
async def remove_organization_member(
    id: uuid.UUID,
    user_id: uuid.UUID,
    _membership: Membership = Depends(require_organization_role(["owner", "admin"])),
    db: AsyncSession = Depends(get_db),
):
    query = select(Membership).where(
        Membership.organization_id == id,
        Membership.user_id == user_id,
    )
    member = (await db.execute(query)).scalar_one_or_none()
    if not member:
        raise NotFoundException("Member not found in organization.")

    if member.role_name == "owner":
        raise AppException("FORBIDDEN", "Cannot remove an organization owner directly.")

    await db.delete(member)
    await db.commit()
    return {"message": "Member removed from organization."}
