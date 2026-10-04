import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Text, BigInteger, Integer, Boolean, ForeignKey, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

from app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin


class KnowledgeBase(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "knowledge_bases"
    __table_args__ = (
        UniqueConstraint("workspace_id", "slug", name="uq_workspace_kb_slug"),
        {"schema": "knowledge"},
    )

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organization.workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)

    # Relationships
    documents: Mapped[List["KnowledgeBaseDocument"]] = relationship("KnowledgeBaseDocument", back_populates="knowledge_base", cascade="all, delete-orphan")


class KnowledgeBaseDocument(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "knowledge_base_documents"
    __table_args__ = (
        UniqueConstraint("knowledge_base_id", "document_id", name="uq_kb_document"),
        {"schema": "knowledge"},
    )

    knowledge_base_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("knowledge.knowledge_bases.id", ondelete="CASCADE"),
        nullable=False,
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("knowledge.documents.id", ondelete="CASCADE"),
        nullable=False,
    )

    knowledge_base: Mapped["KnowledgeBase"] = relationship("KnowledgeBase", back_populates="documents")
    document: Mapped["Document"] = relationship("Document", back_populates="knowledge_bases")


class Document(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "documents"
    __table_args__ = (
        Index("idx_documents_workspace_status", "workspace_id", "status"),
        {"schema": "knowledge"},
    )

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organization.workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)  # pdf, docx, md, txt, etc.
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    file_hash: Mapped[Optional[str]] = mapped_column(String(64), index=True, nullable=True)
    storage_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    current_version_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)  # pending, processing, ready, failed
    deleted_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    # Relationships
    knowledge_bases: Mapped[List["KnowledgeBaseDocument"]] = relationship("KnowledgeBaseDocument", back_populates="document", cascade="all, delete-orphan")
    versions: Mapped[List["DocumentVersion"]] = relationship("DocumentVersion", back_populates="document", cascade="all, delete-orphan")


class DocumentVersion(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "document_versions"
    __table_args__ = (
        UniqueConstraint("document_id", "version_number", name="uq_document_version_number"),
        {"schema": "knowledge"},
    )

    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("knowledge.documents.id", ondelete="CASCADE"),
        nullable=False,
    )
    version_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    storage_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    file_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    total_pages: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    total_chunks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    metadata_json: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    processing_status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)

    document: Mapped["Document"] = relationship("Document", back_populates="versions")
    chunks: Mapped[List["Chunk"]] = relationship("Chunk", back_populates="version", cascade="all, delete-orphan")


class Chunk(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "chunks"
    __table_args__ = (
        Index("idx_chunks_workspace_id", "workspace_id"),
        Index("idx_chunks_version_id", "version_id"),
        {"schema": "knowledge"},
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
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_type: Mapped[str] = mapped_column(String(50), default="paragraph", nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    page_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    section_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    metadata_json: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)

    version: Mapped["DocumentVersion"] = relationship("DocumentVersion", back_populates="chunks")
    embeddings: Mapped[List["ChunkEmbedding"]] = relationship("ChunkEmbedding", back_populates="chunk", cascade="all, delete-orphan")


class ChunkEmbedding(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "chunk_embeddings"
    __table_args__ = (
        Index("idx_chunk_embeddings_model", "model_name"),
        {"schema": "knowledge"},
    )

    chunk_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("knowledge.chunks.id", ondelete="CASCADE"),
        nullable=False,
    )
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    dimensions: Mapped[int] = mapped_column(Integer, default=768, nullable=False)
    # Default to 768 dimensions (compatible with text-embedding-004 / modern models), can be adapted
    embedding: Mapped[List[float]] = mapped_column(Vector(768), nullable=False)

    chunk: Mapped["Chunk"] = relationship("Chunk", back_populates="embeddings")
