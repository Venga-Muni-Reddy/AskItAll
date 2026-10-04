-- Initialize AskItAll PostgreSQL Database with pgvector and Multi-Schema Layout

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Enable UUID extension for UUID generation if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable pg_trgm for fast trigram text/keyword search
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Create all 10 logical schemas defined in DatabaseDesignDoc.md
CREATE SCHEMA IF NOT EXISTS identity;
CREATE SCHEMA IF NOT EXISTS organization;
CREATE SCHEMA IF NOT EXISTS knowledge;
CREATE SCHEMA IF NOT EXISTS ingestion;
CREATE SCHEMA IF NOT EXISTS retrieval;
CREATE SCHEMA IF NOT EXISTS conversation;
CREATE SCHEMA IF NOT EXISTS memory;
CREATE SCHEMA IF NOT EXISTS ai;
CREATE SCHEMA IF NOT EXISTS usage;
CREATE SCHEMA IF NOT EXISTS audit;

-- Set search path to include public and standard schemas
ALTER DATABASE askitall_db SET search_path TO "$user", public, identity, organization, knowledge, ingestion, retrieval, conversation, memory, ai, usage, audit;
