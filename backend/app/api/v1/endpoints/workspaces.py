import uuid
import re
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.exceptions import NotFoundException, ForbiddenException
from app.db.session import get_db
from app.db.models.identity import User
from app.db.models.organization import Organization, Membership, Workspace, WorkspaceMembership
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate, WorkspaceResponse

router = APIRouter()


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-")


@router.get("/organizations/{org_id}/workspaces", response_model=List[WorkspaceResponse])
async def list_workspaces(
    org_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify org access
    org_access = await db.execute(
        select(Membership).where(Membership.organization_id == org_id, Membership.user_id == current_user.id)
    )
    if not org_access.scalar_one_or_none():
        raise ForbiddenException("You do not have access to this organization.")

    query = select(Workspace).where(Workspace.organization_id == org_id)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/organizations/{org_id}/workspaces", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    org_id: uuid.UUID,
    payload: WorkspaceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify org access
    org_access = await db.execute(
        select(Membership).where(Membership.organization_id == org_id, Membership.user_id == current_user.id)
    )
    if not org_access.scalar_one_or_none():
        raise ForbiddenException("You do not have access to this organization.")

    slug = payload.slug or slugify(payload.name)
    existing = await db.execute(
        select(Workspace).where(Workspace.organization_id == org_id, Workspace.slug == slug)
    )
    if existing.scalar_one_or_none():
        slug = f"{slug}-{uuid.uuid4().hex[:6]}"

    workspace = Workspace(
        organization_id=org_id,
        name=payload.name,
        slug=slug,
        description=payload.description,
        status="active",
    )
    db.add(workspace)
    await db.flush()

    # Add creator as workspace admin
    membership = WorkspaceMembership(
        workspace_id=workspace.id,
        user_id=current_user.id,
        role="admin",
    )
    db.add(membership)
    await db.commit()
    await db.refresh(workspace)
    return workspace


@router.get("/workspaces/{id}", response_model=WorkspaceResponse)
async def get_workspace(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(Workspace)
        .join(WorkspaceMembership, WorkspaceMembership.workspace_id == Workspace.id)
        .where(Workspace.id == id, WorkspaceMembership.user_id == current_user.id)
    )
    result = await db.execute(query)
    workspace = result.scalar_one_or_none()
    if not workspace:
        raise NotFoundException("Workspace not found or access denied.")
    return workspace
