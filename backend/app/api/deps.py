import uuid
from typing import Optional, List, Callable
from fastapi import Depends, Header, Path
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UnauthorizedException, ForbiddenException, NotFoundException
from app.core.security import decode_token
from app.db.session import get_db
from app.db.models.identity import User
from app.db.models.organization import Membership, WorkspaceMembership

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not token:
        raise UnauthorizedException("Authentication token is missing.")

    payload = decode_token(token)
    if not payload:
        raise UnauthorizedException("Invalid or expired authentication token.")

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise UnauthorizedException("Token payload missing user identifier.")

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise UnauthorizedException("Malformed user identifier in token.")

    query = select(User).where(User.id == user_id, User.deleted_at.is_(None))
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise UnauthorizedException("User not found or account has been removed.")

    if user.status != "active":
        raise ForbiddenException("User account is suspended or inactive.")

    return user


def require_organization_role(allowed_roles: List[str]):
    """
    Dependency factory to check if the current user has the required role in an organization.
    """
    async def role_checker(
        org_id: uuid.UUID = Path(..., alias="id"),
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> Membership:
        query = select(Membership).where(
            Membership.organization_id == org_id,
            Membership.user_id == current_user.id,
            Membership.status == "active",
        )
        result = await db.execute(query)
        membership = result.scalar_one_or_none()
        if not membership:
            raise ForbiddenException("You are not a member of this organization.")

        if allowed_roles and membership.role_name not in allowed_roles:
            raise ForbiddenException(
                f"Role '{membership.role_name}' does not have sufficient permissions. Required: {', '.join(allowed_roles)}"
            )

        return membership

    return role_checker


def require_workspace_role(allowed_roles: List[str]):
    """
    Dependency factory to check if the current user has the required role in a workspace.
    """
    async def role_checker(
        workspace_id: uuid.UUID = Path(..., alias="id"),
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> WorkspaceMembership:
        query = select(WorkspaceMembership).where(
            WorkspaceMembership.workspace_id == workspace_id,
            WorkspaceMembership.user_id == current_user.id,
        )
        result = await db.execute(query)
        membership = result.scalar_one_or_none()
        if not membership:
            raise ForbiddenException("You are not a member of this workspace.")

        if allowed_roles and membership.role not in allowed_roles:
            raise ForbiddenException(
                f"Role '{membership.role}' does not have sufficient workspace permissions. Required: {', '.join(allowed_roles)}"
            )

        return membership

    return role_checker
