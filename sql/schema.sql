-- ShiftWise PostgreSQL + pgvector Schema

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS chunks (
    id BIGSERIAL PRIMARY KEY,
    version VARCHAR(20) NOT NULL,
    document VARCHAR(500) NOT NULL,
    page INTEGER NOT NULL,
    heading TEXT,
    start_line INTEGER NOT NULL,
    end_line INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding vector(768),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Filters for version locking and document lookups
CREATE INDEX IF NOT EXISTS idx_chunks_version ON chunks(version);
CREATE INDEX IF NOT EXISTS idx_chunks_document ON chunks(document);
CREATE INDEX IF NOT EXISTS idx_chunks_version_page ON chunks(version, document, page);

-- HNSW vector cosine distance index for semantic similarity search
CREATE INDEX IF NOT EXISTS idx_chunks_embedding ON chunks USING hnsw (embedding vector_cosine_ops);

