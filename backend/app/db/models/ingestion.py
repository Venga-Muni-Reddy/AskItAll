import uuid
from typing import Optional, Dict, Any
from sqlalchemy import String, Text, Integer, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin


class CanonicalRepresentation(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "canonical_representations"
    __table_args__ = {"schema": "ingestion"}

    version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("knowledge.document_versions.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    content_json: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    storage_path: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)


class Job(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "jobs"
    __table_args__ = (
        Index("idx_ingestion_jobs_workspace_status", "workspace_id", "status"),
        {"schema": "ingestion"},
    )

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organization.workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("knowledge.documents.id", ondelete="CASCADE"),
        nullable=False,
    )
    version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("knowledge.document_versions.id", ondelete="CASCADE"),
        nullable=False,
    )
    job_type: Mapped[str] = mapped_column(String(50), default="process_document", nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="queued", nullable=False)  # queued, processing, completed, failed
    progress_percent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    current_stage: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class JobEvent(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "job_events"
    __table_args__ = {"schema": "ingestion"}

    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ingestion.jobs.id", ondelete="CASCADE"),
        nullable=False,
    )
    stage: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
