"""PgVector provider for semantic search over file embeddings.

Requires: PostgreSQL + pgvector extension. Falls back to mock on error.
"""
from typing import Any

from src.config import config

from .mock_provider import semantic_search_mock

# Lazy imports for optional deps
_conn = None


def _get_connection():
    """Get PostgreSQL connection (lazy init). Returns None if pgvector unavailable."""
    global _conn
    if _conn is not None:
        return _conn
    try:
        import psycopg2
        from pgvector.psycopg2 import register_vector

        conn = psycopg2.connect(config.DATABASE_URL)
        register_vector(conn)
        _conn = conn
        return conn
    except Exception:
        return None


def _embed_query(query: str) -> list[float]:
    """
    Convert query to embedding vector.
    Mock: returns placeholder. Real: use sentence-transformers or OpenAI.
    """
    return [0.0] * 384  # Placeholder for 384-dim (e.g. all-MiniLM-L6-v2)


def _semantic_search_pgvector(
    query: str,
    tenant_id: str,
    project_id: str,
    top_k: int = 10,
    file_ids: list[str] | None = None,
) -> list[dict[str, Any]]:
    """
    Real pgvector semantic search.
    Expects: chunks (chunk_id, file_id, content_text, page_number, embedding vector(384)), files (tenant_id, project_id).
    """
    conn = _get_connection()
    if conn is None:
        return []

    try:
        embedding = _embed_query(query)
        cur = conn.cursor()
        sql = """
            SELECT c.chunk_id, c.file_id, c.content_text, c.page_number,
                   1 - (c.embedding <=> %s::vector) as similarity
            FROM chunks c
            JOIN files f ON f.file_id = c.file_id
            WHERE f.tenant_id = %s AND f.project_id = %s
        """
        params: list[Any] = [embedding, tenant_id, project_id]
        if file_ids:
            sql += " AND c.file_id = ANY(%s)"
            params.append(file_ids)
        sql += " ORDER BY c.embedding <=> %s::vector LIMIT %s"
        params.extend([embedding, top_k])
        cur.execute(sql, params)
        rows = cur.fetchall()
        cur.close()
        return [
            {
                "chunk_id": r[0],
                "file_id": r[1],
                "content": r[2],
                "page_number": r[3],
                "score": float(r[4]),
                "provenance": {"file_id": r[1], "chunk_id": r[0], "page": r[3]},
            }
            for r in rows
        ]
    except Exception:
        return []


class PgVectorProvider:
    """Provider for pgvector semantic search. Falls back to mock if pgvector unavailable."""

    def semantic_search(
        self,
        query: str,
        tenant_id: str,
        project_id: str,
        top_k: int = 10,
        file_ids: list[str] | None = None,
        threshold: float | None = None,
    ) -> list[dict[str, Any]]:
        results = _semantic_search_pgvector(
            query, tenant_id, project_id, top_k, file_ids
        )
        if not results:
            results = semantic_search_mock(query, tenant_id, project_id, top_k)
        if threshold is not None:
            results = [r for r in results if r.get("score", 0) >= threshold]
        return results
