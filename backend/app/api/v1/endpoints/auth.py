import re
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.config import settings
from app.core.exceptions import ConflictException, UnauthorizedException, AppException
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.db.session import get_db
from app.db.models.identity import User
from app.db.models.organization import (
    Organization,
    Membership,
    Workspace,
    WorkspaceMembership,
)
from app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenRefreshRequest,
    ChangePasswordRequest,
    TokenResponse,
    UserResponse,
    UserMeResponse,
    UserOrgSummary,
    UserWorkspaceSummary,
)

router = APIRouter()


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-") or "workspace"


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    payload: UserRegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    # Check if email is already taken
    query = select(User).where(User.email == payload.email)
    result = await db.execute(query)
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise ConflictException("A user with this email address already exists.")

    hashed_pw = get_password_hash(payload.password)
    user = User(
        email=payload.email,
        password_hash=hashed_pw,
        display_name=payload.display_name,
        status="active",
        email_verified_at=datetime.now(timezone.utc),
    )
    db.add(user)
    await db.flush()

    # If organization_name is provided, set up their primary tenant workspace
    if payload.organization_name:
        org_slug = slugify(payload.organization_name)
        existing_org = await db.execute(select(Organization).where(Organization.slug == org_slug))
        if existing_org.scalar_one_or_none():
            org_slug = f"{org_slug}-{uuid.uuid4().hex[:6]}"

        org = Organization(
            name=payload.organization_name,
            slug=org_slug,
            status="active",
        )
        db.add(org)
        await db.flush()

        # Add user as organization owner
        membership = Membership(
            organization_id=org.id,
            user_id=user.id,
            role_name="owner",
            status="active",
        )
        db.add(membership)

        # Create default workspace
        ws_slug = "primary-workspace"
        workspace = Workspace(
            organization_id=org.id,
            name=f"{payload.organization_name} Primary",
            slug=ws_slug,
            description="Primary organization workspace",
            status="active",
        )
        db.add(workspace)
        await db.flush()

        ws_membership = WorkspaceMembership(
            workspace_id=workspace.id,
            user_id=user.id,
            role="admin",
        )
        db.add(ws_membership)

    await db.commit()
    await db.refresh(user)

    access_token = create_access_token(
        subject=str(user.id),
        extra_claims={"email": user.email, "name": user.display_name},
    )
    refresh_token = create_refresh_token(subject=str(user.id))

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
async def login_user(
    payload: UserLoginRequest,
    db: AsyncSession = Depends(get_db),
):
    query = select(User).where(User.email == payload.email, User.deleted_at.is_(None))
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user or not user.password_hash or not verify_password(payload.password, user.password_hash):
        raise UnauthorizedException("Invalid email or password.")

    if user.status != "active":
        raise UnauthorizedException("Account is not active.")

    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(user)

    access_token = create_access_token(
        subject=str(user.id),
        extra_claims={"email": user.email, "name": user.display_name},
    )
    refresh_token = create_refresh_token(subject=str(user.id))

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    payload: TokenRefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    token_data = decode_token(payload.refresh_token)
    if not token_data or token_data.get("type") != "refresh":
        raise UnauthorizedException("Invalid or expired refresh token.")

    user_id_str = token_data.get("sub")
    query = select(User).where(User.id == user_id_str, User.deleted_at.is_(None))
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user or user.status != "active":
        raise UnauthorizedException("User no longer valid.")

    new_access = create_access_token(
        subject=str(user.id),
        extra_claims={"email": user.email, "name": user.display_name},
    )
    new_refresh = create_refresh_token(subject=str(user.id))

    return TokenResponse(
        access_token=new_access,
        refresh_token=new_refresh,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserMeResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Fetch user's organizations
    org_query = (
        select(Organization, Membership.role_name)
        .join(Membership, Membership.organization_id == Organization.id)
        .where(Membership.user_id == current_user.id, Membership.status == "active")
    )
    org_rows = (await db.execute(org_query)).all()
    org_summaries = [
        UserOrgSummary(
            organization_id=row[0].id,
            name=row[0].name,
            slug=row[0].slug,
            role=row[1],
        )
        for row in org_rows
    ]

    # Fetch user's workspaces
    ws_query = (
        select(Workspace, WorkspaceMembership.role)
        .join(WorkspaceMembership, WorkspaceMembership.workspace_id == Workspace.id)
        .where(WorkspaceMembership.user_id == current_user.id)
    )
    ws_rows = (await db.execute(ws_query)).all()
    ws_summaries = [
        UserWorkspaceSummary(
            workspace_id=row[0].id,
            organization_id=row[0].organization_id,
            name=row[0].name,
            slug=row[0].slug,
            role=row[1],
        )
        for row in ws_rows
    ]

    return UserMeResponse(
        user=UserResponse.model_validate(current_user),
        organizations=org_summaries,
        workspaces=ws_summaries,
    )


@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not current_user.password_hash or not verify_password(payload.current_password, current_user.password_hash):
        raise AppException("INVALID_CREDENTIALS", "Current password does not match.")

    current_user.password_hash = get_password_hash(payload.new_password)
    await db.commit()
    return {"message": "Password updated successfully."}
