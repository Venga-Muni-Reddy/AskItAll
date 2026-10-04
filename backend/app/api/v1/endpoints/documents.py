import hashlib
import os
import uuid
import aiofiles
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.config import settings
from app.core.exceptions import NotFoundException, ForbiddenException, AppException
from app.db.session import get_db
from app.db.models.identity import User
from app.db.models.organization import WorkspaceMembership
from app.db.models.knowledge import Document, DocumentVersion, KnowledgeBaseDocument
from app.db.models.ingestion import Job
from app.schemas.document import DocumentResponse, ProcessingStatusResponse

router = APIRouter()

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md", ".json", ".csv"}


@router.get("/workspaces/{workspace_id}/documents", response_model=List[DocumentResponse])
async def list_documents(
    workspace_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Document).where(
        Document.workspace_id == workspace_id,
        Document.deleted_at.is_(None),
    ).order_by(Document.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/workspaces/{workspace_id}/documents/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    workspace_id: uuid.UUID,
    file: UploadFile = File(...),
    knowledge_base_ids: Optional[List[uuid.UUID]] = Form(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify workspace membership
    membership = await db.execute(
        select(WorkspaceMembership).where(
            WorkspaceMembership.workspace_id == workspace_id,
            WorkspaceMembership.user_id == current_user.id,
        )
    )
    if not membership.scalar_one_or_none():
        raise ForbiddenException("Access to workspace denied.")

    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise AppException(
            code="UNSUPPORTED_FILE_TYPE",
            message=f"File extension '{ext}' is not supported. Supported: {', '.join(ALLOWED_EXTENSIONS)}",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    # Read and compute hash
    content = await file.read()
    file_size = len(content)
    file_hash = hashlib.sha256(content).hexdigest()

    # Storage destination
    dest_dir = os.path.join(settings.LOCAL_STORAGE_DIR, str(workspace_id))
    os.makedirs(dest_dir, exist_ok=True)
    saved_filename = f"{file_hash[:12]}_{file.filename}"
    file_path = os.path.join(dest_dir, saved_filename)

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    clean_file_type = ext.replace(".", "")

    # Create Document record
    doc = Document(
        workspace_id=workspace_id,
        title=file.filename or "Untitled Document",
        original_filename=file.filename or "document",
        file_type=clean_file_type,
        file_size_bytes=file_size,
        file_hash=file_hash,
        storage_path=file_path,
        status="pending",
    )
    db.add(doc)
    await db.flush()

    # Create DocumentVersion record
    version = DocumentVersion(
        document_id=doc.id,
        version_number=1,
        storage_path=file_path,
        file_hash=file_hash,
        processing_status="pending",
    )
    db.add(version)
    await db.flush()

    doc.current_version_id = version.id

    # Associate with Knowledge Bases if provided
    if knowledge_base_ids:
        for kb_id in knowledge_base_ids:
            kb_doc = KnowledgeBaseDocument(
                knowledge_base_id=kb_id,
                document_id=doc.id,
            )
            db.add(kb_doc)

    # Create Ingestion Job record
    job = Job(
        workspace_id=workspace_id,
        document_id=doc.id,
        version_id=version.id,
        job_type="process_document",
        status="queued",
        current_stage="queued",
        progress_percent=0,
    )
    db.add(job)
    await db.commit()
    await db.refresh(doc)

    # Trigger async processing task
    try:
        from app.worker.tasks.ingestion import process_document_task
        process_document_task.delay(str(job.id), str(doc.id), str(version.id), file_path, clean_file_type)
    except Exception:
        # Fallback if celery broker is not reachable in local dev
        pass

    return doc


@router.get("/documents/{id}", response_model=DocumentResponse)
async def get_document(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Document).where(Document.id == id, Document.deleted_at.is_(None))
    result = await db.execute(query)
    doc = result.scalar_one_or_none()
    if not doc:
        raise NotFoundException("Document not found.")
    return doc


@router.get("/documents/{id}/processing-status", response_model=ProcessingStatusResponse)
async def get_document_processing_status(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Job).where(Job.document_id == id).order_by(Job.created_at.desc())
    result = await db.execute(query)
    job = result.scalar_one_or_none()
    if not job:
        raise NotFoundException("No processing job found for this document.")

    return ProcessingStatusResponse(
        document_id=id,
        status=job.status,
        current_stage=job.current_stage,
        progress_percent=job.progress_percent,
        error_message=job.error_message,
    )
