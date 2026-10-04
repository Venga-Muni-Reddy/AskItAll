# Enterprise Multimodal Knowledge Intelligence Platform
## Database Design Document

**Version:** 1.0  
**Status:** Approved  
**Primary Database:** PostgreSQL  
**Vector Store:** PostgreSQL + pgvector  
**Graph Database:** Neo4j  
**Cache / Queue:** Redis  
**Object Storage:** Cloudinary → S3  
**Migration:** Alembic + reviewed SQL  
**Primary ID:** UUIDv7  
**Tenant Isolation:** Application authorization + PostgreSQL RLS

---

# 1. Purpose

This document defines the persistent data architecture for the Enterprise Multimodal Knowledge Intelligence Platform.

It covers:

- PostgreSQL relational model
- PostgreSQL schema organization
- multi-tenancy
- RBAC
- workspace and knowledge-base relationships
- document versioning
- canonical representations
- structural document data
- semantic chunks
- embeddings
- entities and relationships
- conversations
- memory
- citations
- retrieval traces
- usage and AI costs
- audit logging
- pgvector
- Neo4j
- Redis
- object-storage metadata
- deletion and retention
- indexing
- authorization
- migration
- backup/recovery
- scaling

The most important database principle is:

> **PostgreSQL is the authoritative system of record. Vector indexes, graph data, caches, and queues are derived/supporting systems.**

---

# 2. Database Architecture

```text
                           PostgreSQL
                     ┌────────────────────┐
                     │ System of Record   │
                     └─────────┬──────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
          ▼                    ▼                    ▼
       pgvector              Neo4j               Redis
     Vector Search       Knowledge Graph      Cache / Queue
          │                    │                    │
          │                    │                    │
          └────────────────────┼────────────────────┘
                               │
                               ▼
                        Object Storage
                      Cloudinary / S3
```

---

# 3. Source-of-Truth Rules

| Data | Source of Truth |
|---|---|
| Users | PostgreSQL |
| Organizations | PostgreSQL |
| Memberships | PostgreSQL |
| Roles | PostgreSQL |
| Workspaces | PostgreSQL |
| Knowledge Bases | PostgreSQL |
| Documents | PostgreSQL |
| Document versions | PostgreSQL |
| Canonical metadata | PostgreSQL |
| Original files | Object Storage |
| Large canonical artifacts | Object Storage |
| Chunks | PostgreSQL |
| Embeddings | pgvector |
| Entities | PostgreSQL |
| Knowledge graph | Neo4j, derived |
| Conversations | PostgreSQL |
| Messages | PostgreSQL |
| Long-term memory | PostgreSQL |
| Memory embeddings | pgvector |
| Retrieval traces | PostgreSQL |
| AI usage | PostgreSQL |
| Audit logs | PostgreSQL |
| Queue state | Redis/Celery |
| Cache | Redis |

---

# 4. PostgreSQL Schema Organization

The database should use logical PostgreSQL schemas rather than placing everything in `public`.

```text
PostgreSQL
│
├── identity
├── organization
├── knowledge
├── ingestion
├── retrieval
├── conversation
├── memory
├── ai
├── usage
└── audit
```

This is a logical organization mechanism, not a requirement that every schema become a separate service.

---

# 5. Identity Schema

## 5.1 `identity.users`

Stores platform identities.

```text
identity.users
--------------
id                  UUID PK
email               CITEXT UNIQUE
email_verified_at   TIMESTAMPTZ NULL
password_hash       TEXT NULL
display_name        TEXT
avatar_url          TEXT NULL
status              USER_STATUS
last_login_at       TIMESTAMPTZ NULL
created_at          TIMESTAMPTZ
updated_at          TIMESTAMPTZ
deleted_at          TIMESTAMPTZ NULL
```

### Notes

`password_hash` is nullable because OAuth users may not have a local password.

`CITEXT` is useful for case-insensitive email uniqueness.

---

# 6. Authentication Identities

## `identity.user_identities`

Supports multiple authentication mechanisms.

```text
identity.user_identities
------------------------
id
user_id FK → identity.users.id
provider
provider_subject
created_at
updated_at
```

Example:

```text
User
 ├── password
 ├── Google OAuth
 └── Microsoft OAuth
```

Unique constraint:

```text
(provider, provider_subject)
```

---

# 7. Organizations

## `organization.organizations`

```text
organization.organizations
--------------------------
id
name
slug
status
settings JSONB
created_at
updated_at
deleted_at
```

Unique:

```text
slug
```

---

# 8. Organization Membership

## `organization.memberships`

```text
organization.memberships
------------------------
id
organization_id FK
user_id FK
role_id FK
status
created_at
updated_at
```

Unique:

```text
organization_id + user_id
```

This supports:

```text
User A
 ├── Organization X → Admin
 ├── Organization Y → Member
 └── Organization Z → Viewer
```

---

# 9. Roles

Because V1 uses fixed roles but must support custom RBAC later, roles should still be represented as data.

## `organization.roles`

```text
organization.roles
------------------
id
organization_id FK NULL
scope
name
system_role
description
created_at
updated_at
```

`organization_id = NULL` can represent system-defined roles.

Example:

```text
SYSTEM:
OWNER
ADMIN
MEMBER

CUSTOM:
Security Reviewer
Knowledge Manager
```

This allows custom roles later without redesigning membership.

---

# 10. Permissions

## `organization.permissions`

```text
organization.permissions
-----------------------
id
code
description
```

Examples:

```text
organization.read
organization.manage
workspace.read
workspace.write
knowledge_base.read
knowledge_base.write
document.read
document.upload
document.delete
conversation.read
conversation.delete
usage.read
audit.read
```

---

# 11. Role Permissions

## `organization.role_permissions`

```text
organization.role_permissions
-----------------------------
role_id FK
permission_id FK
```

Composite primary key:

```text
(role_id, permission_id)
```

Therefore:

```text
Role
 ↓
Permissions
```

This gives us fixed V1 roles while leaving a path toward custom RBAC.

---

# 12. Workspace Schema

## `organization.workspaces`

```text
organization.workspaces
-----------------------
id
organization_id FK
name
slug
description
settings JSONB
status
created_at
updated_at
deleted_at
```

Unique:

```text
organization_id + slug
```

Relationship:

```text
Organization
   │
   ├── Workspace A
   ├── Workspace B
   └── Workspace C
```

---

# 13. Workspace Membership

## `organization.workspace_memberships`

```text
organization.workspace_memberships
----------------------------------
id
workspace_id FK
user_id FK
role_id FK
status
created_at
updated_at
```

Unique:

```text
workspace_id + user_id
```

---

# 14. Knowledge Base

## `knowledge.knowledge_bases`

```text
knowledge.knowledge_bases
-------------------------
id
workspace_id FK
name
slug
description
status
settings JSONB
created_by FK
created_at
updated_at
deleted_at
```

Relationship:

```text
Workspace
   │
   ├── Knowledge Base A
   ├── Knowledge Base B
   └── Knowledge Base C
```

A knowledge base belongs to exactly one workspace.

---

# 15. Knowledge Base Membership

Although KB access can initially inherit workspace permissions, explicit membership should be possible.

## `knowledge.knowledge_base_memberships`

```text
id
knowledge_base_id FK
user_id FK
role_id FK
created_at
updated_at
```

Unique:

```text
knowledge_base_id + user_id
```

This gives the authorization system flexibility without introducing chunk-level permissions.

---

# 16. Documents

## `knowledge.documents`

```text
knowledge.documents
-------------------
id
organization_id FK
workspace_id FK
title
source_type
mime_type
file_name
status
current_version_id FK NULL
created_by FK
metadata JSONB
created_at
updated_at
deleted_at
```

Important:

The document directly references its organization and workspace.

This avoids requiring authorization queries to traverse:

```text
Document
 → KB
 → Workspace
 → Organization
```

for every operation.

---

# 17. Document ↔ Knowledge Base

## `knowledge.knowledge_base_documents`

```text
knowledge.knowledge_base_documents
-----------------------------------
knowledge_base_id FK
document_id FK
created_at
```

Composite primary key:

```text
knowledge_base_id + document_id
```

Therefore:

```text
Document A
 ├── KB Finance
 ├── KB Research
 └── KB Strategy
```

without duplicating the actual document.

---

# 18. Document Versions

## `knowledge.document_versions`

```text
knowledge.document_versions
----------------------------
id
document_id FK
version_number
checksum
file_size_bytes
mime_type
original_file_name
object_storage_key
parser_name
parser_version
processing_status
processing_error JSONB NULL
created_by FK
created_at
completed_at
```

Unique:

```text
document_id + version_number
```

Each version is independent.

```text
Document
 ├── Version 1
 ├── Version 2
 └── Version 3
```

Each version receives its own:

- canonical representation
- structural content
- chunks
- embeddings
- graph provenance.

---

# 19. Why Version Data Is Independent

Suppose Version 1 contains:

```text
Revenue = ₹100 crore
```

and Version 2 contains:

```text
Revenue = ₹120 crore
```

Their chunks and embeddings must not accidentally overlap in a way that causes the old version to masquerade as the current version.

Therefore:

```text
Version 1
   ↓
Chunks V1
   ↓
Embeddings V1

Version 2
   ↓
Chunks V2
   ↓
Embeddings V2
```

This simplifies correctness.

---

# 20. Canonical Representation

## `ingestion.canonical_representations`

```text
ingestion.canonical_representations
------------------------------------
id
document_version_id FK
schema_version
object_storage_key
content_hash
metadata JSONB
created_at
```

The large canonical representation is stored in object storage.

PostgreSQL stores:

- manifest
- schema version
- storage key
- hash
- searchable metadata.

---

# 21. Document Structure

The document hierarchy should use a hybrid model.

Important structural elements receive relational records.

---

## `knowledge.sections`

```text
knowledge.sections
------------------
id
document_version_id FK
parent_section_id FK NULL
section_type
title
ordinal
source_location JSONB
metadata JSONB
created_at
```

Supports:

```text
Document
 ├── Section
 │    ├── Subsection
 │    └── Subsection
 └── Section
```

---

# 22. Paragraphs

## `knowledge.paragraphs`

```text
knowledge.paragraphs
--------------------
id
section_id FK
document_version_id FK
ordinal
content
source_location JSONB
metadata JSONB
created_at
```

---

# 23. Tables

## `knowledge.tables`

```text
knowledge.tables
----------------
id
document_version_id FK
section_id FK NULL
title
ordinal
source_location JSONB
metadata JSONB
created_at
```

Table cells/rows can be represented in structured JSON initially.

Future high-volume table workloads can introduce normalized row/cell structures.

---

# 24. Images

## `knowledge.images`

```text
knowledge.images
----------------
id
document_version_id FK
section_id FK NULL
object_storage_key
mime_type
width
height
caption
ocr_text
description
source_location JSONB
metadata JSONB
created_at
```

This supports future multimodal retrieval.

---

# 25. Charts and Diagrams

Charts and diagrams should have their own content types.

Possible table:

```text
knowledge.visual_elements
-------------------------
id
document_version_id
section_id
type
object_storage_key
description
extracted_text
source_location JSONB
metadata JSONB
```

`type`:

```text
chart
diagram
figure
equation
drawing
```

This prevents the schema from becoming unnecessarily fragmented.

---

# 26. Semantic Chunks

## `knowledge.chunks`

```text
knowledge.chunks
----------------
id
document_version_id FK
section_id FK NULL
paragraph_id FK NULL
parent_chunk_id FK NULL
chunk_type
content
ordinal
token_count
source_location JSONB
metadata JSONB
created_at
```

A chunk can therefore retain its structural ancestry.

```text
Chunk
 ├── Document Version
 ├── Section
 ├── Paragraph
 └── Parent Chunk
```

---

# 27. Chunk Metadata

`metadata JSONB` can contain:

```json
{
  "page_number": 42,
  "language": "en",
  "modality": "text",
  "entities": [],
  "relationships": [],
  "parser_metadata": {}
}
```

Frequently queried attributes should eventually receive dedicated columns/indexes instead of being permanently buried in JSONB.

---

# 28. Chunk Embeddings

## `knowledge.chunk_embeddings`

```text
knowledge.chunk_embeddings
--------------------------
id
chunk_id FK
embedding_model
provider
dimensions
embedding vector
created_at
```

Unique:

```text
chunk_id + embedding_model
```

This supports:

```text
Chunk
 ├── embedding-model-A
 └── embedding-model-B
```

without changing the chunk table.

---

# 29. Embedding Model Registry

## `ai.embedding_models`

```text
ai.embedding_models
-------------------
id
provider
model_name
dimensions
max_input_tokens
status
configuration JSONB
created_at
updated_at
```

This avoids scattering model names throughout the database.

---

# 30. Vector Indexing

The vector column uses pgvector.

Conceptually:

```text
knowledge.chunk_embeddings.embedding
```

The index strategy should be selected based on dataset size and workload.

For V1:

```text
PostgreSQL
 +
pgvector
 +
appropriate ANN index
```

As data volume grows significantly:

```text
VectorStore abstraction
        ↓
Dedicated vector database
```

can replace the implementation.

---

# 31. Entities

## `knowledge.entities`

```text
knowledge.entities
------------------
id
organization_id FK
canonical_name
entity_type
description
metadata JSONB
created_at
updated_at
```

Examples:

```text
PERSON
ORGANIZATION
PRODUCT
LOCATION
EVENT
TECHNOLOGY
CONCEPT
```

---

# 32. Entity Aliases

## `knowledge.entity_aliases`

```text
knowledge.entity_aliases
------------------------
id
entity_id FK
alias
normalized_alias
created_at
```

Example:

```text
Canonical Entity:
OpenAI

Aliases:
OpenAI
OpenAI Inc.
OpenAI, Inc.
```

---

# 33. Entity Mentions

## `knowledge.entity_mentions`

```text
knowledge.entity_mentions
-------------------------
id
entity_id FK
document_version_id FK
chunk_id FK
text
source_location JSONB
confidence
created_at
```

This separates:

```text
Entity identity
```

from:

```text
Where the entity was mentioned
```

---

# 34. Knowledge Facts

## `knowledge.facts`

```text
knowledge.facts
---------------
id
organization_id
subject_entity_id
predicate
object_entity_id NULL
object_value JSONB NULL
confidence
status
created_at
updated_at
```

This can represent:

```text
Company A
    │
    └── acquired → Company B
```

or:

```text
Company A
    │
    └── revenue → ₹100 crore
```

---

# 35. Fact Provenance

## `knowledge.fact_provenance`

```text
knowledge.fact_provenance
-------------------------
id
fact_id FK
document_id FK
document_version_id FK
chunk_id FK NULL
source_location JSONB
extraction_method
confidence
created_at
```

This is critical.

Every important knowledge graph fact should be traceable back to evidence.

---

# 36. Graph Architecture

Neo4j is a derived representation.

```text
PostgreSQL
   │
   │ authoritative facts/entities/provenance
   ▼
Graph Builder
   │
   ▼
Neo4j
```

Neo4j should not become an untraceable second source of truth.

---

# 37. Neo4j Node Model

Core nodes:

```text
(:Organization)
(:Person)
(:Product)
(:Location)
(:Event)
(:Concept)
(:Document)
(:DocumentVersion)
(:Chunk)
(:Fact)
```

Example:

```text
(:Person {
    entity_id: "..."
})
```

---

# 38. Neo4j Relationship Model

Examples:

```text
(:Person)-[:WORKS_FOR]->(:Organization)

(:Organization)-[:ACQUIRED]->(:Organization)

(:Person)-[:MENTIONED_IN]->(:Document)

(:Document)-[:HAS_VERSION]->(:DocumentVersion)

(:DocumentVersion)-[:CONTAINS]->(:Chunk)

(:Chunk)-[:MENTIONS]->(:Entity)
```

Relationships should include identifiers needed to connect them to PostgreSQL provenance.

---

# 39. Graph Synchronization

Graph synchronization should be asynchronous.

```text
PostgreSQL
    ↓
Graph Change / Job
    ↓
Celery
    ↓
Graph Builder
    ↓
Neo4j
```

If Neo4j becomes unavailable:

```text
PostgreSQL remains operational.
```

Graph-dependent queries can degrade gracefully where possible.

---

# 40. Conversation Schema

## `conversation.conversations`

```text
conversation.conversations
--------------------------
id
user_id FK
organization_id FK
workspace_id FK
title
scope_type
settings JSONB
created_at
updated_at
deleted_at
```

---

# 41. Conversation Scope

A conversation can support:

```text
ALL_ACCESSIBLE_KBS
KNOWLEDGE_BASE
DOCUMENT
```

Additional scope IDs can be represented through a separate table.

---

# 42. Conversation Scopes

## `conversation.conversation_scopes`

```text
conversation.conversation_scopes
---------------------------------
id
conversation_id FK
scope_type
knowledge_base_id FK NULL
document_id FK NULL
created_at
```

Example:

```text
Conversation
 ├── KB A
 ├── KB B
 └── Document X
```

This makes the scope explicit.

---

# 43. Messages

## `conversation.messages`

```text
conversation.messages
---------------------
id
conversation_id FK
role
content
model
provider
input_tokens
output_tokens
latency_ms
metadata JSONB
created_at
```

Roles:

```text
system
user
assistant
tool
```

Messages are the source of truth for conversation history.

---

# 44. Message Citations

## `conversation.message_citations`

```text
conversation.message_citations
------------------------------
id
message_id FK
document_id FK
document_version_id FK
chunk_id FK NULL
source_location JSONB
citation_text
created_at
```

This creates:

```text
Assistant Message
       │
       ├── Citation → Document A
       ├── Citation → Document B
       └── Citation → Table C
```

---

# 45. Retrieval Traces

## `retrieval.retrieval_traces`

```text
retrieval.retrieval_traces
--------------------------
id
conversation_id FK NULL
message_id FK NULL
query
strategy JSONB
candidate_count
created_at
completed_at
```

---

# 46. Retrieval Candidates

## `retrieval.retrieval_candidates`

```text
retrieval.retrieval_candidates
------------------------------
id
trace_id FK
chunk_id FK NULL
entity_id FK NULL
fact_id FK NULL
retrieval_method
retrieval_score
rerank_score NULL
rank_before
rank_after
metadata JSONB
created_at
```

This supports evaluation of:

- vector retrieval
- keyword retrieval
- graph retrieval
- reranking.

---

# 47. Configurable Retrieval Trace

Because detailed traces can generate substantial storage:

```text
Workspace
   ↓
retrieval_trace_policy
```

Possible:

```text
NONE
FINAL_ONLY
DETAILED
```

Production debugging/evaluation environments can use detailed traces.

---

# 48. Memory

## `memory.memories`

```text
memory.memories
---------------
id
organization_id FK NULL
workspace_id FK NULL
user_id FK NULL
conversation_id FK NULL
memory_type
content
importance
source
status
expires_at NULL
metadata JSONB
created_at
updated_at
deleted_at
```

This allows memories at different ownership scopes.

---

# 49. Memory Types

Examples:

```text
USER_PREFERENCE
WORKSPACE_CONTEXT
CONVERSATION_SUMMARY
TASK_CONTEXT
FACT
```

Memory visibility must be explicitly determined from ownership.

---

# 50. Memory Embeddings

## `memory.memory_embeddings`

```text
memory.memory_embeddings
------------------------
id
memory_id FK
embedding_model
dimensions
embedding vector
created_at
```

Only memories useful for semantic retrieval need embeddings.

---

# 51. AI Gateway Configuration

## `ai.model_providers`

```text
ai.model_providers
------------------
id
name
provider_type
status
configuration JSONB
created_at
updated_at
```

Credentials should not be stored directly in ordinary database records.

Use a secrets-management system.

---

# 52. Models

## `ai.models`

```text
ai.models
---------
id
provider_id FK
model_name
model_type
context_window
capabilities JSONB
pricing JSONB
status
created_at
updated_at
```

`model_type`:

```text
LLM
EMBEDDING
RERANKER
VISION
AUDIO
```

---

# 53. Workspace AI Policies

## `ai.workspace_policies`

```text
ai.workspace_policies
---------------------
id
workspace_id FK
default_llm_id FK
default_embedding_model_id FK
default_reranker_id FK
privacy_policy
configuration JSONB
created_at
updated_at
```

This implements:

```text
Workspace
   ↓
AI Policy
```

---

# 54. AI Request Records

## `ai.ai_requests`

```text
ai.ai_requests
--------------
id
organization_id FK
workspace_id FK NULL
user_id FK NULL
provider_id FK
model_id FK
operation
input_tokens
output_tokens
latency_ms
estimated_cost
status
trace_id
metadata JSONB
created_at
```

Examples:

```text
EMBEDDING
LLM_GENERATION
RERANKING
OCR
VISION_ANALYSIS
```

---

# 55. Usage Schema

## `usage.usage_events`

```text
usage.usage_events
------------------
id
organization_id FK
workspace_id FK NULL
user_id FK NULL
event_type
quantity
unit
estimated_cost
resource_id
metadata JSONB
created_at
```

Examples:

```text
DOCUMENT_PROCESSED
EMBEDDING_TOKENS
LLM_INPUT_TOKENS
LLM_OUTPUT_TOKENS
STORAGE_BYTES
QUERY
RERANKER_CALL
OCR_PAGE
```

---

# 56. Usage Aggregates

Raw usage events provide flexibility, while aggregate tables make dashboards efficient.

Possible:

```text
usage.daily_usage
-----------------
organization_id
workspace_id
date
documents_processed
embedding_tokens
llm_input_tokens
llm_output_tokens
queries
storage_bytes
estimated_cost
```

This can be generated asynchronously from raw events.

---

# 57. Audit Schema

## `audit.audit_logs`

```text
audit.audit_logs
----------------
id
organization_id FK
workspace_id FK NULL
actor_user_id FK NULL
action
resource_type
resource_id
result
ip_address
user_agent
metadata JSONB
created_at
```

Audit records are append-only.

The application should not expose generic update/delete APIs for audit records.

---

# 58. Ingestion Jobs

## `ingestion.jobs`

```text
ingestion.jobs
--------------
id
document_id FK
document_version_id FK
job_type
status
current_stage
attempt_count
last_error JSONB
started_at
completed_at
created_at
updated_at
```

---

# 59. Processing Stages

Possible values:

```text
UPLOADED
SCANNING
SCANNED
PARSING
PARSED
CANONICALIZING
CANONICALIZED
CHUNKING
CHUNKED
EMBEDDING
EMBEDDED
ENTITY_EXTRACTION
GRAPH_BUILDING
INDEXING
READY
FAILED
```

---

# 60. Ingestion Stage History

## `ingestion.job_events`

```text
ingestion.job_events
--------------------
id
job_id FK
stage
status
message
metadata JSONB
created_at
```

This gives us an operational history without putting every state transition directly into the document table.

---

# 61. Redis Data Model

Redis is not the authoritative database.

It is used for:

- Celery queues
- temporary processing state
- caching
- rate limiting
- short-lived locks.

Potential keys:

```text
cache:user:{user_id}
cache:workspace:{workspace_id}
cache:kb:{kb_id}

lock:document:{document_id}

ratelimit:user:{user_id}
ratelimit:organization:{organization_id}
```

TTL should be defined for cache keys.

---

# 62. Celery Queue Model

Recommended queues:

```text
celery
│
├── ingestion
├── parsing
├── ocr
├── chunking
├── embeddings
├── graph
├── cleanup
├── notifications
└── maintenance
```

Large workloads should be isolated into dedicated workers.

---

# 63. Object Storage Metadata

Object storage keys should be deterministic and version-aware.

Example:

```text
organizations/{org_id}/
    documents/{document_id}/
        versions/{version_id}/
            original/
            canonical/
            images/
            tables/
            derived/
```

Example:

```text
organizations/
  org_123/
    documents/
      doc_456/
        versions/
          ver_789/
            original/source.pdf
            canonical/document.json
            images/page-001.png
```

This prevents collisions and makes cleanup easier.

---

# 64. Object Storage References

PostgreSQL stores references:

```text
object_storage_key
storage_provider
content_type
size_bytes
checksum
```

It does not assume whether the provider is:

```text
Cloudinary
S3
```

The provider abstraction remains in the application layer.

---

# 65. Authorization Data Flow

Authorization is enforced before retrieval.

```text
User
 ↓
Authentication
 ↓
Organization membership
 ↓
Workspace membership
 ↓
KB membership / inherited permission
 ↓
Document authorization
 ↓
Authorized document IDs
 ↓
Retrieval
```

The retrieval system must receive authorized scopes as part of the query plan.

---

# 66. RLS Strategy

PostgreSQL RLS should protect tenant-owned records.

Conceptually:

```text
current_user
     ↓
application sets tenant context
     ↓
PostgreSQL RLS
     ↓
only permitted rows
```

RLS should be designed carefully around connection pooling so tenant context cannot leak between requests.

---

# 67. Authorization and pgvector

Vector searches must include authorization constraints.

Conceptually:

```sql
SELECT ...
FROM knowledge.chunk_embeddings ce
JOIN knowledge.chunks c ON ...
JOIN knowledge.documents d ON ...
WHERE d.organization_id = :organization_id
  AND d.workspace_id IN (...)
  AND d.deleted_at IS NULL;
```

The vector similarity operation must not happen over an unrestricted tenant-wide dataset followed by application-side filtering.

---

# 68. Authorization and Neo4j

Graph queries must also carry authorization scope.

Example conceptual constraint:

```text
Query
 ↓
Authorized document IDs
 ↓
Graph traversal
 ↓
Only permitted graph evidence
```

The graph layer must not return a relationship simply because the relationship itself is visible if its source document is unauthorized.

---

# 69. Soft Delete Rules

Soft deletion applies to major user-owned entities.

Examples:

```text
Organization
Workspace
Knowledge Base
Document
Conversation
Memory
```

But not every table needs `deleted_at`.

For example:

- join tables can often be physically removed
- ephemeral job records can follow retention
- audit logs are append-only.

---

# 70. Document Deletion Flow

```text
DELETE document
       │
       ▼
Set documents.deleted_at
       │
       ▼
Remove from normal retrieval scope
       │
       ▼
Create cleanup job
       │
       ├── PostgreSQL chunks
       ├── embeddings
       ├── entities/mentions where applicable
       ├── Neo4j relationships
       ├── object storage
       └── derived artifacts
```

Physical cleanup is asynchronous.

---

# 71. Referential Integrity

Foreign keys should be used extensively.

However, cascading deletes should be used selectively.

For critical enterprise data:

```text
Application-controlled deletion
```

is preferable to allowing a single accidental `DELETE` to cascade through thousands of records.

---

# 72. Unique Constraints

Important examples:

```text
users.email

organization.slug

organization_memberships:
    organization_id + user_id

workspace_memberships:
    workspace_id + user_id

knowledge_base_documents:
    knowledge_base_id + document_id

document_versions:
    document_id + version_number

chunk_embeddings:
    chunk_id + embedding_model

entity_aliases:
    normalized_alias + organization_id
```

---

# 73. Index Strategy

Important relational indexes:

```text
users(email)

organization_memberships(user_id)
organization_memberships(organization_id)

workspaces(organization_id)

knowledge_bases(workspace_id)

documents(organization_id)
documents(workspace_id)
documents(status)
documents(deleted_at)

document_versions(document_id)

sections(document_version_id)

paragraphs(document_version_id)
paragraphs(section_id)

chunks(document_version_id)
chunks(section_id)

messages(conversation_id, created_at)

memories(user_id)
memories(workspace_id)

audit_logs(organization_id, created_at)

usage_events(organization_id, created_at)
```

---

# 74. JSONB Strategy

JSONB is intended for flexible metadata, not as a replacement for relational modeling.

Good JSONB candidates:

```text
parser_metadata
source_location
document_metadata
visual_metadata
AI configuration
provider configuration
retrieval strategy
processing errors
```

Poor candidates:

```text
organization_id
user_id
document_id
created_at
status
foreign keys
```

Frequently queried relational properties should have proper columns/indexes.

---

# 75. Time Data

Use:

```text
TIMESTAMPTZ
```

for timestamps.

Store timestamps in UTC.

The frontend can convert them to the user's local timezone.

---

# 76. Status Values

Statuses should be implemented through controlled values.

Depending on the migration strategy, these may use:

- PostgreSQL enums for highly stable values
- check constraints
- lookup tables
- application enums

For fast-changing product states, lookup/check constraints may be preferable to excessive PostgreSQL enum proliferation.

---

# 77. ER Relationship Overview

The major relational structure is:

```text
User
 │
 ├──────────────┐
 ▼              ▼
Organization   Workspace Membership
 │
 ├── Memberships
 │
 └── Workspaces
        │
        ├── Workspace Members
        │
        └── Knowledge Bases
                 │
                 ├── KB Members
                 │
                 └── Documents ◄──────────────┐
                                                │
Document ──────────────────────────────────────┘
   │
   └── Document Versions
          │
          ├── Canonical Representation
          ├── Sections
          ├── Paragraphs
          ├── Tables
          ├── Images
          └── Chunks
                 │
                 └── Chunk Embeddings
```

---

# 78. Knowledge Relationship Overview

```text
Document Version
      │
      ├── Chunk
      │     │
      │     └── Entity Mention
      │
      ├── Entity
      │
      └── Fact
             │
             └── Fact Provenance
```

Neo4j derives its graph from these relationships.

---

# 79. Conversation Relationship Overview

```text
User
 │
 └── Conversation
       │
       ├── Scope
       │
       └── Messages
              │
              └── Citations
                     │
                     └── Document Version
```

---

# 80. Memory Relationship Overview

```text
User
 │
 └── Memory
       │
       └── Memory Embedding
```

A memory can additionally belong to:

```text
Organization
Workspace
Conversation
```

depending on its scope.

---

# 81. Data Lifecycle

The overall lifecycle is:

```text
Upload
  ↓
Document
  ↓
Version
  ↓
Security Scan
  ↓
Canonical Representation
  ↓
Structure Extraction
  ↓
Chunks
  ↓
Embeddings
  ↓
Entities
  ↓
Facts
  ↓
Neo4j
  ↓
Ready for Retrieval
```

Deletion reverses the derived-data dependency:

```text
Logical Delete
  ↓
Remove Retrieval Visibility
  ↓
Async Cleanup
  ├── pgvector
  ├── chunks
  ├── graph
  ├── object storage
  └── derived artifacts
```

---

# 82. Database Migration Strategy

Alembic is the primary migration tool.

Example:

```text
alembic/
    versions/
        001_initial_identity.py
        002_organizations.py
        003_workspaces.py
        004_knowledge.py
        005_documents.py
        006_chunks.py
        007_embeddings.py
        008_conversations.py
        ...
```

Complex database operations may use reviewed SQL inside Alembic migrations.

---

# 83. Migration Rules

Every migration should be:

- version controlled
- reversible where practical
- tested against representative data
- reviewed
- applied in CI/CD eventually
- safe for production deployment.

For large tables, avoid blocking migrations.

Use expand/contract patterns:

```text
Add new structure
      ↓
Backfill
      ↓
Switch application
      ↓
Remove old structure
```

---

# 84. Backup Strategy

PostgreSQL:

```text
Automated backup
+
Point-in-time recovery
```

Neo4j:

```text
Scheduled backup
```

Object storage:

```text
Versioning
+
Lifecycle policies
+
Optional replication
```

Redis:

```text
Not authoritative
```

Loss of Redis should not mean loss of business data.

---

# 85. Disaster Recovery Principle

Recovery order:

```text
1. PostgreSQL
       ↓
2. Object Storage
       ↓
3. Redis reconstruction
       ↓
4. Neo4j reconstruction
       ↓
5. Derived vector indexes
```

This is possible because the architecture deliberately establishes PostgreSQL and object storage as authoritative foundations.

---

# 86. Rebuilding Derived Stores

If pgvector indexes are lost:

```text
PostgreSQL chunks
       ↓
Embedding service
       ↓
Rebuild embeddings
```

If Neo4j is lost:

```text
PostgreSQL entities/facts/provenance
       ↓
Graph Builder
       ↓
Neo4j reconstruction
```

If Redis is lost:

```text
Recreate queues/cache
```

This is a major reliability advantage of the architecture.

---

# 87. Scaling PostgreSQL

Initially:

```text
Single PostgreSQL
+
pgvector
```

Later:

```text
Primary
 ├── Read replicas
 └── Backups
```

If data volume becomes very large:

```text
Partition large event tables
```

Potential candidates:

- audit logs
- usage events
- retrieval traces
- AI request logs.

---

# 88. Partitioning Strategy

Do not partition everything from day one.

Partition only when data volume justifies it.

Likely candidates:

```text
audit.audit_logs
usage.usage_events
retrieval.retrieval_traces
ai.ai_requests
```

Time-based partitioning can be appropriate:

```text
2026-01
2026-02
2026-03
...
```

---

# 89. Large-Scale Vector Evolution

V1:

```text
PostgreSQL
   +
pgvector
```

At scale:

```text
VectorStore
     │
     ├── PgVectorStore
     └── DedicatedVectorStore
```

Possible future implementations:

```text
Qdrant
Milvus
```

The application does not directly depend on the selected vendor.

---

# 90. Database Design and RAG Correctness

The schema intentionally preserves the complete chain:

```text
Answer
 ↓
Citation
 ↓
Chunk
 ↓
Document Version
 ↓
Document
 ↓
Original File
```

And for graph knowledge:

```text
Answer
 ↓
Fact
 ↓
Fact Provenance
 ↓
Chunk
 ↓
Document Version
 ↓
Original File
```

This makes evidence traceability possible.

---

# 91. Important Design Rule: Version-Aware Retrieval

Retrieval should never treat all document versions as equivalent.

The query layer should explicitly decide whether to retrieve:

```text
CURRENT_ONLY
```

or:

```text
ALL_VERSIONS
```

or:

```text
SPECIFIC_VERSION
```

For normal enterprise Q&A:

```text
CURRENT_ONLY
```

should generally be the default.

Historical questions can explicitly search older versions.

---

# 92. Important Design Rule: Current Version Pointer

The document contains:

```text
current_version_id
```

This is a denormalized convenience pointer.

The authoritative version records still exist independently.

Whenever a new version becomes current:

```text
document.current_version_id
        ↓
new version
```

and retrieval indexes should be updated accordingly.

---

# 93. Important Design Rule: No Physical Duplication Across KBs

If:

```text
Document A
```

belongs to:

```text
KB 1
KB 2
KB 3
```

we do **not** create:

```text
Document A1
Document A2
Document A3
```

Instead:

```text
Document A
     │
     ├── KB 1
     ├── KB 2
     └── KB 3
```

This saves:

- storage
- embedding cost
- processing cost
- synchronization complexity.

---

# 94. Important Design Rule: Authorization Before Search

The data model enables:

```text
User
 ↓
Accessible organizations
 ↓
Accessible workspaces
 ↓
Accessible KBs
 ↓
Accessible documents
 ↓
Retrieval
```

This is not merely an API-level concern.

The database relationships and indexes must support efficient authorization-aware filtering.

---

# 95. Future Custom RBAC

V1:

```text
OWNER
ADMIN
MEMBER
VIEWER
```

Later:

```text
Security Analyst
Knowledge Manager
Compliance Reviewer
External Auditor
```

without redesigning the membership model.

The evolution becomes:

```text
User
 ↓
Membership
 ↓
Role
 ↓
Permissions
```

rather than hard-coding role checks throughout the application.

---

# 96. Future Enterprise SSO

The current identity model supports:

```text
Email/password
OAuth
```

Later:

```text
OIDC
SAML
SCIM
Enterprise directory
```

The important decision is that authentication identities are separated from the core `users` table.

---

# 97. Future Multimodal Extensions

The database already leaves room for:

```text
Audio
Video
Frames
Timestamps
Speakers
OCR
Visual Elements
```

Future tables can extend:

```text
knowledge.visual_elements
knowledge.media_segments
knowledge.speakers
knowledge.transcripts
knowledge.temporal_chunks
```

without changing the fundamental document/version/chunk architecture.

---

# 98. Future Connector Architecture

External sources can map into the same document model.

Example:

```text
Google Drive
     ↓
Connector
     ↓
Document
     ↓
Document Version
     ↓
Canonical Representation
     ↓
Chunks / Graph / Embeddings
```

The source can be recorded as:

```text
source_type = GOOGLE_DRIVE
```

rather than requiring a completely different database architecture.

---

# 99. Database Design Principles

The implementation should follow these principles:

### 1. Normalize authoritative business data.

### 2. Use JSONB for flexible metadata, not core relationships.

### 3. Keep derived indexes rebuildable.

### 4. Preserve document version boundaries.

### 5. Preserve evidence provenance.

### 6. Enforce tenant isolation at multiple layers.

### 7. Never depend on Redis as authoritative storage.

### 8. Avoid premature database partitioning.

### 9. Avoid premature dedicated vector infrastructure.

### 10. Keep vendor-specific infrastructure behind abstractions.

---

# 100. Final Data Architecture

The final architecture can be summarized as:

```text
                         ┌──────────────────────┐
                         │      PostgreSQL      │
                         │   AUTHORITATIVE DB   │
                         └──────────┬───────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
   Business Data               Knowledge Data              AI Data
        │                           │                           │
        ├── Users                   ├── Documents               ├── Models
        ├── Organizations           ├── Versions                ├── AI Requests
        ├── Memberships             ├── Sections                ├── Policies
        ├── Roles                   ├── Chunks                  └── Costs
        ├── Workspaces              ├── Entities
        └── Permissions             └── Facts
                                    │
                    ┌───────────────┴──────────────┐
                    ▼                              ▼
                pgvector                         Neo4j
             Semantic Index                 Derived Graph
                    │                              │
                    └───────────────┬──────────────┘
                                    │
                                    ▼
                              RAG Retrieval


             ┌────────────────────────────────────────┐
             │            Other Persistence            │
             ├────────────────────────────────────────┤
             │ Redis → cache / queues / locks         │
             │ Object Storage → files / artifacts     │
             └────────────────────────────────────────┘
```

---

# 101. Final Ownership Model

```text
                 SOURCE OF TRUTH
                       │
                       ▼
                 PostgreSQL
                       │
          ┌────────────┼─────────────┐
          │            │             │
          ▼            ▼             ▼
       pgvector      Neo4j         Object Storage
       derived       derived       source artifacts
          │            │             │
          └────────────┼─────────────┘
                       │
                       ▼
                   Retrieval
                       │
                       ▼
                    AI Layer
```

The architecture deliberately ensures that the system can survive the loss or replacement of a derived technology.

---

# 102. Final Decision

The database architecture is therefore:

```text
PostgreSQL
 ├── identity
 ├── organization
 ├── knowledge
 ├── ingestion
 ├── retrieval
 ├── conversation
 ├── memory
 ├── ai
 ├── usage
 └── audit

        +
        
pgvector

        +

Neo4j

        +

Redis

        +

Cloudinary / S3
```

with:

```text
UUIDv7
+
RLS
+
Application Authorization
+
Versioning
+
Provenance
+
Hybrid JSONB/relational modeling
+
Rebuildable derived stores
+
Extensible RBAC
+
Multi-tenant isolation
```

This provides a strong V1 database foundation while preserving the evolution path toward enterprise-scale multimodal knowledge intelligence.