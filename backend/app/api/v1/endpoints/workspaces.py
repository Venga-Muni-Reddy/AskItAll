import uuid
import re
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_workspace_role
from app.core.exceptions import NotFoundException, ForbiddenException, ConflictException, AppException
from app.db.session import get_db
from app.db.models.identity import User
from app.db.models.organization import (
    Organization,
    Membership,
    Workspace,
    WorkspaceMembership,
)
from app.schemas.workspace import (
    WorkspaceCreate,
    WorkspaceUpdate,
    WorkspaceResponse,
    WorkspaceMemberAdd,
    WorkspaceMemberUpdate,
    WorkspaceMemberWithUser,
)

router = APIRouter()


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-") or "workspace"


@router.get("/organizations/{org_id}/workspaces", response_model=List[WorkspaceResponse])
async def list_workspaces(
    org_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify org access
    org_access = await db.execute(
        select(Membership).where(
            Membership.organization_id == org_id,
            Membership.user_id == current_user.id,
            Membership.status == "active",
        )
    )
    if not org_access.scalar_one_or_none():
        raise ForbiddenException("You do not have access to this organization.")

    # Get workspaces and the user's role in each
    query = (
        select(Workspace, WorkspaceMembership.role)
        .outerjoin(
            WorkspaceMembership,
            (WorkspaceMembership.workspace_id == Workspace.id) & (WorkspaceMembership.user_id == current_user.id),
        )
        .where(Workspace.organization_id == org_id, Workspace.status != "deleted")
        .order_by(Workspace.created_at.desc())
    )
    result = await db.execute(query)
    rows = result.all()

    return [
        WorkspaceResponse(
            id=ws.id,
            organization_id=ws.organization_id,
            name=ws.name,
            slug=ws.slug,
            description=ws.description,
            status=ws.status,
            user_role=role or "member",
            created_at=ws.created_at,
        )
        for ws, role in rows
    ]


@router.post("/organizations/{org_id}/workspaces", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    org_id: uuid.UUID,
    payload: WorkspaceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    org_access = await db.execute(
        select(Membership).where(
            Membership.organization_id == org_id,
            Membership.user_id == current_user.id,
            Membership.role_name.in_(["owner", "admin"]),
            Membership.status == "active",
        )
    )
    if not org_access.scalar_one_or_none():
        raise ForbiddenException("You need Owner or Admin privileges in this organization to create a workspace.")

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

    return WorkspaceResponse(
        id=workspace.id,
        organization_id=workspace.organization_id,
        name=workspace.name,
        slug=workspace.slug,
        description=workspace.description,
        status=workspace.status,
        user_role="admin",
        created_at=workspace.created_at,
    )


@router.get("/workspaces/{id}", response_model=WorkspaceResponse)
async def get_workspace(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(Workspace, WorkspaceMembership.role)
        .join(WorkspaceMembership, WorkspaceMembership.workspace_id == Workspace.id)
        .where(Workspace.id == id, WorkspaceMembership.user_id == current_user.id, Workspace.status != "deleted")
    )
    result = await db.execute(query)
    row = result.first()
    if not row:
        raise NotFoundException("Workspace not found or access denied.")
    ws, role = row

    return WorkspaceResponse(
        id=ws.id,
        organization_id=ws.organization_id,
        name=ws.name,
        slug=ws.slug,
        description=ws.description,
        status=ws.status,
        user_role=role,
        created_at=ws.created_at,
    )


@router.patch("/workspaces/{id}", response_model=WorkspaceResponse)
async def update_workspace(
    id: uuid.UUID,
    payload: WorkspaceUpdate,
    _membership: WorkspaceMembership = Depends(require_workspace_role(["admin"])),
    db: AsyncSession = Depends(get_db),
):
    ws = await db.get(Workspace, id)
    if not ws:
        raise NotFoundException("Workspace not found.")

    if payload.name:
        ws.name = payload.name
    if payload.description is not None:
        ws.description = payload.description

    await db.commit()
    await db.refresh(ws)

    return WorkspaceResponse(
        id=ws.id,
        organization_id=ws.organization_id,
        name=ws.name,
        slug=ws.slug,
        description=ws.description,
        status=ws.status,
        user_role=_membership.role,
        created_at=ws.created_at,
    )


@router.delete("/workspaces/{id}", status_code=status.HTTP_200_OK)
async def delete_workspace(
    id: uuid.UUID,
    _membership: WorkspaceMembership = Depends(require_workspace_role(["admin"])),
    db: AsyncSession = Depends(get_db),
):
    ws = await db.get(Workspace, id)
    if not ws:
        raise NotFoundException("Workspace not found.")
    ws.status = "deleted"
    await db.commit()
    return {"message": "Workspace deactivated successfully."}


@router.get("/workspaces/{id}/members", response_model=List[WorkspaceMemberWithUser])
async def list_workspace_members(
    id: uuid.UUID,
    _membership: WorkspaceMembership = Depends(require_workspace_role(["admin", "member", "viewer"])),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(WorkspaceMembership, User)
        .join(User, User.id == WorkspaceMembership.user_id)
        .where(WorkspaceMembership.workspace_id == id)
        .order_by(WorkspaceMembership.created_at.asc())
    )
    result = await db.execute(query)
    rows = result.all()

    return [
        WorkspaceMemberWithUser(
            membership_id=m.id,
            workspace_id=m.workspace_id,
            user_id=u.id,
            email=u.email,
            display_name=u.display_name,
            role=m.role,
            joined_at=m.created_at,
        )
        for m, u in rows
    ]


@router.post("/workspaces/{id}/members", response_model=WorkspaceMemberWithUser, status_code=status.HTTP_201_CREATED)
async def add_workspace_member(
    id: uuid.UUID,
    payload: WorkspaceMemberAdd,
    _membership: WorkspaceMembership = Depends(require_workspace_role(["admin"])),
    db: AsyncSession = Depends(get_db),
):
    target_user: User | None = None
    if payload.email:
        target_user = (await db.execute(select(User).where(User.email == payload.email))).scalar_one_or_none()
    elif payload.user_id:
        target_user = await db.get(User, payload.user_id)

    if not target_user:
        raise NotFoundException("User not found.")

    # Check if already a member
    existing = await db.execute(
        select(WorkspaceMembership).where(
            WorkspaceMembership.workspace_id == id,
            WorkspaceMembership.user_id == target_user.id,
        )
    )
    if existing.scalar_one_or_none():
        raise ConflictException("User is already a member of this workspace.")

    new_member = WorkspaceMembership(
        workspace_id=id,
        user_id=target_user.id,
        role=payload.role,
    )
    db.add(new_member)
    await db.commit()
    await db.refresh(new_member)

    return WorkspaceMemberWithUser(
        membership_id=new_member.id,
        workspace_id=id,
        user_id=target_user.id,
        email=target_user.email,
        display_name=target_user.display_name,
        role=new_member.role,
        joined_at=new_member.created_at,
    )


@router.patch("/workspaces/{id}/members/{user_id}", response_model=WorkspaceMemberWithUser)
async def update_workspace_member_role(
    id: uuid.UUID,
    user_id: uuid.UUID,
    payload: WorkspaceMemberUpdate,
    _membership: WorkspaceMembership = Depends(require_workspace_role(["admin"])),
    db: AsyncSession = Depends(get_db),
):
    query = select(WorkspaceMembership, User).join(User, User.id == WorkspaceMembership.user_id).where(
        WorkspaceMembership.workspace_id == id,
        WorkspaceMembership.user_id == user_id,
    )
    row = (await db.execute(query)).first()
    if not row:
        raise NotFoundException("Workspace member not found.")
    m, u = row

    m.role = payload.role
    await db.commit()

    return WorkspaceMemberWithUser(
        membership_id=m.id,
        workspace_id=id,
        user_id=u.id,
        email=u.email,
        display_name=u.display_name,
        role=m.role,
        joined_at=m.created_at,
    )


@router.delete("/workspaces/{id}/members/{user_id}", status_code=status.HTTP_200_OK)
async def remove_workspace_member(
    id: uuid.UUID,
    user_id: uuid.UUID,
    _membership: WorkspaceMembership = Depends(require_workspace_role(["admin"])),
    db: AsyncSession = Depends(get_db),
):
    query = select(WorkspaceMembership).where(
        WorkspaceMembership.workspace_id == id,
        WorkspaceMembership.user_id == user_id,
    )
    member = (await db.execute(query)).scalar_one_or_none()
    if not member:
        raise NotFoundException("Member not found in workspace.")

    await db.delete(member)
    await db.commit()
    return {"message": "Member removed from workspace."}
