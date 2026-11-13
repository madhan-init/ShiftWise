from __future__ import annotations

import json
from typing import Any

from app.config import get_settings


def init_vector_db(database_url: str | None = None) -> None:
    """Create vector extension and chunks table if they do not exist."""
    import psycopg
    from pgvector.psycopg import register_vector

    db_url = database_url or get_settings().database_url
    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            register_vector(conn)
            cur.execute(
                """
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

                CREATE INDEX IF NOT EXISTS idx_chunks_version ON chunks(version);
                CREATE INDEX IF NOT EXISTS idx_chunks_document ON chunks(document);
                CREATE INDEX IF NOT EXISTS idx_chunks_version_page ON chunks(version, document, page);
                CREATE INDEX IF NOT EXISTS idx_chunks_embedding
                    ON chunks USING hnsw (embedding vector_cosine_ops);
                """
            )
            conn.commit()


def insert_chunks(chunks: list[dict[str, Any]], database_url: str | None = None) -> int:
    """Bulk insert parsed chunks with embeddings into PostgreSQL."""
    import psycopg
    from pgvector.psycopg import register_vector

    db_url = database_url or get_settings().database_url
    inserted = 0
    with psycopg.connect(db_url) as conn:
        register_vector(conn)
        with conn.cursor() as cur:
            for c in chunks:
                cur.execute(
                    """
                    INSERT INTO chunks (
                        version, document, page, heading, start_line, end_line, content, embedding, metadata
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
                    """,
                    (
                        c["version"],
                        c["document"],
                        c["page"],
                        c.get("heading"),
                        c["start_line"],
                        c["end_line"],
                        c["content"],
                        c.get("embedding"),
                        json.dumps(c.get("metadata", {})),
                    ),
                )
                inserted += 1
            conn.commit()
    return inserted


def search_chunks(
    query_embedding: list[float],
    *,
    version: str | None = None,
    top_k: int = 5,
    database_url: str | None = None,
) -> list[dict[str, Any]]:
    """Perform cosine similarity search on chunks, optionally filtered by version."""
    import psycopg
    from pgvector.psycopg import register_vector

    db_url = database_url or get_settings().database_url
    with psycopg.connect(db_url) as conn:
        register_vector(conn)
        with conn.cursor() as cur:
            if version:
                cur.execute(
                    """
                    SELECT id, version, document, page, heading, start_line, end_line, content,
                           1 - (embedding <=> %s) AS score, metadata
                    FROM chunks
                    WHERE version = %s
                    ORDER BY embedding <=> %s
                    LIMIT %s;
                    """,
                    (query_embedding, version, query_embedding, top_k),
                )
            else:
                cur.execute(
                    """
                    SELECT id, version, document, page, heading, start_line, end_line, content,
                           1 - (embedding <=> %s) AS score, metadata
                    FROM chunks
                    ORDER BY embedding <=> %s
                    LIMIT %s;
                    """,
                    (query_embedding, query_embedding, top_k),
                )
            rows = cur.fetchall()
            return [
                {
                    "id": r[0],
                    "version": r[1],
                    "document": r[2],
                    "page": r[3],
                    "heading": r[4],
                    "start_line": r[5],
                    "end_line": r[6],
                    "content": r[7],
                    "score": float(r[8]),
                    "metadata": r[9],
                }
                for r in rows
            ]
