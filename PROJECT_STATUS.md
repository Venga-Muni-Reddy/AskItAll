# AskItAll — Project Status & Roadmap Tracker

**Product:** AskItAll — Enterprise Multimodal Knowledge Intelligence Platform  
**Repository:** `https://github.com/Venga-Muni-Reddy/AskItAll`  
**Current Milestone:** Phase 1 — Feature 1 Implementation  
**Last Updated:** October 4, 2026  

---

## 📊 High-Level Roadmap Overview

| Phase | Milestone / Feature | Status | Target Delivery |
| :--- | :--- | :---: | :--- |
| **Phase 0** | **Environment, Docker & Project Scaffold** | ✅ Completed | Oct 4, 2026 |
| **Phase 1** | **Feature 1: Identity, Multi-Tenancy & Access Control** | 🟡 Up Next | In Progress |
| **Phase 2** | **Feature 2: Knowledge Bases & Universal Document Ingestion** | ⚪ Planned | Next |
| **Phase 3** | **Feature 3: Semantic Chunking, Embeddings & Vector Indexing** | ⚪ Planned | Next |
| **Phase 4** | **Feature 4: Hybrid Retrieval Engine (Vector + Keyword + RRF)** | ⚪ Planned | Next |
| **Phase 5** | **Feature 5: Knowledge Graph (Neo4j Entity & Fact Linking)** | ⚪ Planned | Next |
| **Phase 6** | **Feature 6: AI Gateway, Grounded Q&A & Citation Validation** | ⚪ Planned | Next |
| **Phase 7** | **Feature 7: Enterprise Frontend UI & Live Streaming Chat** | ⚪ Planned | Next |
| **Phase 8** | **Feature 8: Observability, Usage Accounting & Audit Logs** | ⚪ Planned | Next |

---

## 🛠️ Phase-by-Phase Detailed Tracking

### ✅ Phase 0: Project Scaffold & Environment Setup (Completed)
- [x] Git repository initialized and pushed to `origin/main`.
- [x] Docker Compose multi-service topology configured:
  - `postgres` (with `pgvector:pg16`, `uuid-ossp`, `pg_trgm`)
  - `redis` (task broker and cache on mapped port 6380)
  - `neo4j` (graph database with APOC on ports 7474 & 7687)
  - `backend` (FastAPI modular core)
  - `celery_worker` (async background workers)
  - `frontend` (React + TypeScript + Vite + Tailwind CSS)
- [x] All 10 PostgreSQL schemas defined and auto-initialized:
  `identity`, `organization`, `knowledge`, `ingestion`, `retrieval`, `conversation`, `memory`, `ai`, `usage`, `audit`.
- [x] Initial models, schemas, and endpoints tested and responding (`/health` & `/docs`).

---

### 🟡 Phase 1: Feature 1 — Identity, Multi-Tenancy & Access Control (Next)

**Goal:** Establish enterprise identity, tenant isolation, and role-based access control (RBAC).

#### Planned Tasks:
- [ ] **Authentication Engine:**
  - [ ] User registration with password strength validation and bcrypt hashing.
  - [ ] JWT authentication (access tokens + secure refresh token rotation).
  - [ ] Session revocation & user profile management (`/auth/me`, `/auth/change-password`).
- [ ] **Multi-Tenant Hierarchy:**
  - [ ] Organization creation and management (Owners, Admins, Members).
  - [ ] Workspace provisioning within Organizations (`org_id` $\rightarrow$ `workspace_id`).
  - [ ] Workspace memberships and user role assignments (`admin`, `member`, `viewer`).
- [ ] **Security & Authorization Middleware:**
  - [ ] Fast dependency injection to enforce Organization and Workspace boundaries.
  - [ ] Pre-flight checks preventing unauthorized tenant data access.
- [ ] **Automated Tests:**
  - [ ] Unit & integration tests for Auth & Multi-Tenancy endpoints.

---

### ⚪ Phase 2: Feature 2 — Knowledge Bases & Universal Document Ingestion
- [ ] Knowledge Base CRUD and access control within workspaces.
- [ ] Direct file upload handler (PDF, DOCX, TXT, MD).
- [ ] File security pipeline (MIME type verification, file hash SHA-256 deduplication).
- [ ] Deterministic Parser Plugins:
  - [ ] PDF parser with page and layout extraction.
  - [ ] DOCX parser with paragraph and table preservation.
  - [ ] Markdown / Text parser with header hierarchy.
- [ ] Canonical JSON representation storage.
- [ ] Async Celery job orchestration with granular progress tracking (`queued` $\rightarrow$ `parsing` $\rightarrow$ `chunking` $\rightarrow$ `embedding` $\rightarrow$ `completed`).

---

### ⚪ Phase 3: Feature 3 — Semantic Chunking, Embeddings & Vector Indexing
- [ ] Structure-aware semantic chunking (preserving headers, tables, lists, and page offsets).
- [ ] Token count calculation and chunk boundary optimization.
- [ ] AI Gateway Embedding Service:
  - [ ] Google Gemini (`text-embedding-004`)
  - [ ] OpenAI (`text-embedding-3-small`)
  - [ ] Local deterministic fallback vector generator.
- [ ] `pgvector` HNSW index configuration for sub-millisecond similarity search.
- [ ] Immutable Document Version linking (chunks bound to `version_id`).

---

### ⚪ Phase 4: Feature 4 — Hybrid Retrieval Engine
- [ ] Dense vector cosine similarity search via pgvector (`<=>`).
- [ ] Sparse keyword search (PostgreSQL full-text search / `pg_trgm`).
- [ ] Reciprocal Rank Fusion (RRF) combining dense and sparse candidate scores.
- [ ] Pre-retrieval authorization filter (guaranteeing search operates strictly within authorized workspace/KBs).
- [ ] Cross-encoder reranking integration.

---

### ⚪ Phase 5: Feature 5 — Knowledge Graph Layer (Neo4j)
- [ ] Entity extraction (Entities, Aliases, Mentions) from parsed documents.
- [ ] Fact extraction (Subject $\rightarrow$ Predicate $\rightarrow$ Object) with provenance links.
- [ ] Neo4j graph synchronization from PostgreSQL worker pipeline.
- [ ] Graph traversal query helpers for multi-hop enterprise entity queries.

---

### ⚪ Phase 6: Feature 6 — AI Gateway, Grounded Chat & Citation Engine
- [ ] Query understanding and intent planner.
- [ ] Context engineering (token budget management, context compression).
- [ ] AI Gateway multi-model routing (Gemini 1.5 Pro, GPT-4o, Claude 3.5 Sonnet, Ollama).
- [ ] **Zero-Hallucination Guardrail:** Deterministic insufficient evidence detection.
- [ ] Citation Validation Engine: Verifies all inline citations `[1]`, `[2]` against source chunks.
- [ ] Server-Sent Events (SSE) streaming chat endpoint (`/chat/stream`).

---

### ⚪ Phase 7: Feature 7 — Enterprise Frontend UI
- [ ] Modern dark-mode dashboard with Tailwind CSS & Lucide icons.
- [ ] Workspace & Knowledge Base switcher.
- [ ] Drag-and-drop document upload manager with real-time progress bars.
- [ ] Interactive Grounded Chat with SSE streaming and markdown rendering.
- [ ] Slide-over Citation Inspector displaying verbatim quote, page, and section.
- [ ] Hybrid Search pool explorer.

---

### ⚪ Phase 8: Feature 8 — Observability, Accounting & Audit
- [ ] Token and cost accounting per workspace and user.
- [ ] Audit logging for all document actions, role changes, and queries.
- [ ] Retrieval trace explorer (query latency, candidate counts, rerank scores).
- [ ] Health checks and metrics dashboard.
