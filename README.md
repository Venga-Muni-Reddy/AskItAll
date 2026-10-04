# AskItAll — Enterprise Multimodal Knowledge Intelligence Platform

AskItAll is an enterprise knowledge platform that ingests unstructured and structured organizational assets (PDF, DOCX, Markdown, Text, Spreadsheets), extracts semantic layout, tables, and relationships, and delivers evidence-grounded Q&A with verifiable citations.

---

## 🏛️ System Architecture

- **Backend**: FastAPI (Python 3.11+) modular core (REST + SSE streaming + WebSockets)
- **Frontend**: React + TypeScript + Vite + Tailwind CSS
- **System of Record**: PostgreSQL 16 (10 isolated schemas: `identity`, `organization`, `knowledge`, `ingestion`, `retrieval`, `conversation`, `memory`, `ai`, `usage`, `audit`)
- **Vector Engine**: `pgvector` (HNSW cosine similarity indexing)
- **Graph Store**: Neo4j (Entity and relationship graph)
- **Queue & Cache**: Redis + Celery workers
- **AI Gateway**: Unified multi-provider abstraction (Google Gemini, OpenAI, Ollama, local fallback)

---

## 🚀 Getting Started

### 1. Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 20+

### 2. Environment Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Provide API keys (such as `GEMINI_API_KEY` or `OPENAI_API_KEY`) if you wish to use cloud models. The platform will automatically fall back to deterministic local mock vectors if no key is supplied.

### 3. Running with Docker Compose
Start all services (PostgreSQL + pgvector, Redis, Neo4j, FastAPI Backend, Celery Worker, and Vite Frontend):
```bash
docker compose up --build
```

- **Frontend App**: `http://localhost:5173`
- **FastAPI Documentation**: `http://localhost:8000/docs`
- **Neo4j Browser**: `http://localhost:7474`

---

## 📂 Directory Layout

```text
AskItAll/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # REST endpoints (auth, orgs, workspaces, docs, search, chat)
│   │   ├── core/            # Security, JWT, Middleware, Exceptions
│   │   ├── db/              # Multi-schema SQLAlchemy models & session
│   │   ├── schemas/         # Pydantic validation schemas
│   │   ├── services/        # AI Gateway, Hybrid Retriever, Citation Engine
│   │   └── worker/          # Celery tasks for async parsing & embedding
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/      # UI components & citation inspector
│   │   ├── services/        # Axios API client
│   │   ├── App.tsx          # Enterprise dashboard & grounded chat
│   │   └── index.css        # Tailwind styling & dark glassmorphism
│   ├── Dockerfile
│   └── package.json
├── docker/
│   └── postgres/init.sql    # Database schemas & pgvector initializer
├── docker-compose.yml       # Full stack container orchestration
└── .env.example             # Configuration template
```
