import os
import uuid
import asyncio
from typing import List, Dict, Any
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.worker.celery_app import celery_app
from app.db.session import sync_engine
from app.db.models.knowledge import Document, DocumentVersion, Chunk, ChunkEmbedding
from app.db.models.ingestion import Job, JobEvent, CanonicalRepresentation
from app.services.ai_gateway.base import AIGateway


def extract_text_from_file(file_path: str, file_type: str) -> List[Dict[str, Any]]:
    """
    Parses document into pages/sections.
    """
    pages = []
    if file_type == "pdf":
        try:
            import pypdf
            reader = pypdf.PdfReader(file_path)
            for idx, page in enumerate(reader.pages):
                txt = page.extract_text() or ""
                if txt.strip():
                    pages.append({"page": idx + 1, "text": txt})
        except Exception as e:
            pages.append({"page": 1, "text": f"Error parsing PDF: {e}"})

    elif file_type == "docx":
        try:
            import docx
            doc = docx.Document(file_path)
            full_text = "\n\n".join([p.text for p in doc.paragraphs if p.text.strip()])
            pages.append({"page": 1, "text": full_text})
        except Exception as e:
            pages.append({"page": 1, "text": f"Error parsing DOCX: {e}"})

    else:
        # Markdown, TXT, CSV, JSON
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                pages.append({"page": 1, "text": content})
        except Exception as e:
            pages.append({"page": 1, "text": f"Error reading file: {e}"})

    return pages


def chunk_text(pages: List[Dict[str, Any]], chunk_size: int = 600, overlap: int = 100) -> List[Dict[str, Any]]:
    """
    Structure-aware chunker preserving page numbers.
    """
    chunks = []
    chunk_idx = 0

    for p in pages:
        page_num = p["page"]
        text = p["text"]
        paragraphs = [para.strip() for para in text.split("\n\n") if para.strip()]

        current_chunk = ""
        for para in paragraphs:
            if len(current_chunk) + len(para) > chunk_size and len(current_chunk) > 100:
                chunks.append({
                    "chunk_index": chunk_idx,
                    "page_number": page_num,
                    "content": current_chunk.strip(),
                    "chunk_type": "paragraph",
                })
                chunk_idx += 1
                current_chunk = para
            else:
                current_chunk += ("\n\n" if current_chunk else "") + para

        if current_chunk.strip():
            chunks.append({
                "chunk_index": chunk_idx,
                "page_number": page_num,
                "content": current_chunk.strip(),
                "chunk_type": "paragraph",
            })
            chunk_idx += 1

    return chunks


async def generate_and_save_embeddings(session: Session, chunk_objs: List[Chunk]):
    for c in chunk_objs:
        vec = await AIGateway.generate_embedding(c.content)
        embedding_obj = ChunkEmbedding(
            chunk_id=c.id,
            model_name="default",
            dimensions=len(vec),
            embedding=vec,
        )
        session.add(embedding_obj)


@celery_app.task(name="process_document_task")
def process_document_task(job_id_str: str, doc_id_str: str, version_id_str: str, file_path: str, file_type: str):
    job_id = uuid.UUID(job_id_str)
    doc_id = uuid.UUID(doc_id_str)
    version_id = uuid.UUID(version_id_str)

    with Session(sync_engine) as session:
        job = session.get(Job, job_id)
        if not job:
            return

        try:
            # 1. Stage: Parsing
            job.current_stage = "parsing"
            job.progress_percent = 20
            job.status = "processing"
            session.commit()

            pages = extract_text_from_file(file_path, file_type)

            # Store Canonical Representation
            canonical = CanonicalRepresentation(
                version_id=version_id,
                content_json={"pages": pages, "total_pages": len(pages)},
                storage_path=file_path,
            )
            session.add(canonical)
            session.commit()

            # 2. Stage: Chunking
            job.current_stage = "chunking"
            job.progress_percent = 50
            session.commit()

            raw_chunks = chunk_text(pages)
            chunk_objs = []
            for r in raw_chunks:
                c = Chunk(
                    workspace_id=job.workspace_id,
                    document_id=doc_id,
                    version_id=version_id,
                    chunk_index=r["chunk_index"],
                    content=r["content"],
                    chunk_type=r["chunk_type"],
                    page_number=r["page_number"],
                    token_count=len(r["content"].split()),
                    metadata_json={},
                )
                session.add(c)
                chunk_objs.append(c)

            session.commit()
            for c in chunk_objs:
                session.refresh(c)

            # 3. Stage: Embedding Generation
            job.current_stage = "embedding"
            job.progress_percent = 80
            session.commit()

            asyncio.run(generate_and_save_embeddings(session, chunk_objs))

            # 4. Finalize
            job.current_stage = "completed"
            job.progress_percent = 100
            job.status = "completed"

            # Update Document and Version status
            doc = session.get(Document, doc_id)
            if doc:
                doc.status = "ready"

            ver = session.get(DocumentVersion, version_id)
            if ver:
                ver.processing_status = "completed"
                ver.total_pages = len(pages)
                ver.total_chunks = len(chunk_objs)

            session.commit()

        except Exception as exc:
            session.rollback()
            job = session.get(Job, job_id)
            if job:
                job.status = "failed"
                job.error_message = str(exc)
            doc = session.get(Document, doc_id)
            if doc:
                doc.status = "failed"
            session.commit()
            raise exc
