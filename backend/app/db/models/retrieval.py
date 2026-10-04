import uuid
from typing import Optional, Dict, Any, List
from sqlalchemy import String, Text, Float, Integer, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin


class RetrievalTrace(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "retrieval_traces"
    __table_args__ = (
        Index("idx_retrieval_traces_workspace", "workspace_id"),
        {"schema": "retrieval"},
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
    conversation_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversation.conversations.id", ondelete="SET NULL"),
        nullable=True,
    )
    query: Mapped[str] = mapped_column(Text, nullable=False)
    strategy_used: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    candidate_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    returned_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    execution_time_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    candidates: Mapped[List["RetrievalCandidate"]] = relationship("RetrievalCandidate", back_populates="trace", cascade="all, delete-orphan")


class RetrievalCandidate(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "retrieval_candidates"
    __table_args__ = {"schema": "retrieval"}

    trace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("retrieval.retrieval_traces.id", ondelete="CASCADE"),
        nullable=False,
    )
    chunk_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("knowledge.chunks.id", ondelete="CASCADE"),
        nullable=False,
    )
    retrieval_source: Mapped[str] = mapped_column(String(50), nullable=False)  # dense, sparse, graph
    initial_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    rerank_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    selected_for_context: Mapped[bool] = mapped_column(default=False, nullable=False)

    trace: Mapped["RetrievalTrace"] = relationship("RetrievalTrace", back_populates="candidates")
