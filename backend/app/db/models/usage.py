import uuid
from sqlalchemy import String, BigInteger, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin


class UsageEvent(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "usage_events"
    __table_args__ = (
        Index("idx_usage_events_workspace_type", "workspace_id", "event_type"),
        {"schema": "usage"},
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organization.organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organization.workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("identity.users.id", ondelete="CASCADE"),
        nullable=False,
    )
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)  # llm_tokens, storage_bytes, retrieval_queries
    quantity: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)  # tokens, bytes, count
