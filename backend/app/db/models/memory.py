import uuid
from typing import Optional, List
from sqlalchemy import String, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

from app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin


class Memory(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "memories"
    __table_args__ = (
        Index("idx_memories_workspace_user", "workspace_id", "user_id"),
        {"schema": "memory"},
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
        ForeignKey("conversation.conversations.id", ondelete="CASCADE"),
        nullable=True,
    )
    memory_type: Mapped[str] = mapped_column(String(50), default="summary", nullable=False)  # summary, entity_fact, user_preference
    content: Mapped[str] = mapped_column(Text, nullable=False)

    embeddings: Mapped[List["MemoryEmbedding"]] = relationship("MemoryEmbedding", back_populates="memory", cascade="all, delete-orphan")


class MemoryEmbedding(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "memory_embeddings"
    __table_args__ = {"schema": "memory"}

    memory_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("memory.memories.id", ondelete="CASCADE"),
        nullable=False,
    )
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    embedding: Mapped[List[float]] = mapped_column(Vector(768), nullable=False)

    memory: Mapped["Memory"] = relationship("Memory", back_populates="embeddings")
