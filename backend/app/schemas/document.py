import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class DocumentResponse(BaseModel):
    id: uuid.UUID
    workspace_id: uuid.UUID
    title: str
    original_filename: str
    file_type: str
    file_size_bytes: int
    current_version_id: Optional[uuid.UUID] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentVersionResponse(BaseModel):
    id: uuid.UUID
    document_id: uuid.UUID
    version_number: int
    total_pages: int
    total_chunks: int
    processing_status: str
    metadata_json: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentUploadInitRequest(BaseModel):
    filename: str
    file_size_bytes: int
    knowledge_base_ids: List[uuid.UUID] = []


class DocumentUploadInitResponse(BaseModel):
    document_id: uuid.UUID
    upload_url: str
    upload_id: str
    storage_type: str  # local, s3, cloudinary


class ProcessingStatusResponse(BaseModel):
    document_id: uuid.UUID
    status: str
    current_stage: str
    progress_percent: int
    error_message: Optional[str] = None
