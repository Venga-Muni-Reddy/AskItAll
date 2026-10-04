import uuid
from typing import Optional, Dict, Any
from sqlalchemy import String, Integer, Boolean, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin


class ModelProvider(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "model_providers"
    __table_args__ = {"schema": "ai"}

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)  # google, openai, anthropic, ollama
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Model(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "models"
    __table_args__ = {"schema": "ai"}

    provider_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ai.model_providers.id", ondelete="CASCADE"),
        nullable=False,
    )
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    model_type: Mapped[str] = mapped_column(String(50), nullable=False)  # llm, embedding, reranker
    context_window: Mapped[int] = mapped_column(Integer, default=8192, nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class WorkspacePolicy(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "workspace_policies"
    __table_args__ = {"schema": "ai"}

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organization.workspaces.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    allowed_providers: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    max_tokens_per_request: Mapped[int] = mapped_column(Integer, default=4096, nullable=False)
    privacy_policy_level: Mapped[str] = mapped_column(String(50), default="standard", nullable=False)


class AIRequest(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "ai_requests"
    __table_args__ = (
        Index("idx_ai_requests_workspace", "workspace_id"),
        {"schema": "ai"},
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
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="success", nullable=False)
