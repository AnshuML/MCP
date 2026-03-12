"""PgVector provider for semantic search over document_embeddings.

Schema: document_embeddings (chunk_id, document_id, tenant_id, content, embedding vector(3072)).
Uses Ollama for query embeddings. Tenant-isolated.
"""
import logging
from typing import Any

from src.config import config
from src.embedding.ollama_client import get_query_embedding

from .mock_provider import semantic_search_mock

logger = logging.getLogger(__name__)

_conn = None


def _get_connection():
    """Get PostgreSQL connection with pgvector. Returns None if unavailable."""
    global _conn
    if _conn is not None:
        try:
            _conn.rollback()
            _conn.cursor().execute("SELECT 1")
            return _conn
        except Exception:
            _conn = None
    try:
        import psycopg2
        from pgvector.psycopg2 import register_vector

        conn = psycopg2.connect(config.DATABASE_URL)
        conn.autocommit = True  # Must be outside transaction for register_vector
        register_vector(conn)
        _conn = conn
        return conn
    except Exception as e:
        logger.exception("pgvector connection failed: %s", e)
        return None


def _semantic_search_pgvector(
    query: str,
    tenant_id: str,
    project_id: str,
    top_k: int = 10,
    file_ids: list[str] | None = None,
    threshold: float | None = None,
) -> list[dict[str, Any]]:
    """
    Semantic search over document_embeddings.
    Schema: chunk_id, document_id, tenant_id, content, embedding vector(3072), metadata.
    """
    embedding = get_query_embedding(query)
    if embedding is None:
        logger.warning("Embedding unavailable, falling back to mock")
        return semantic_search_mock(query, tenant_id, project_id, top_k)

    conn = _get_connection()
    if conn is None:
        return semantic_search_mock(query, tenant_id, project_id, top_k)

    try:
        # pgvector accepts vector as string "[x,y,z,...]" for ::vector cast
        embedding_str = "[" + ",".join(str(float(x)) for x in embedding) + "]"
        cur = conn.cursor()
        sql = """
            SELECT e.chunk_id, e.document_id, e.content, e.metadata,
                   1 - (e.embedding <=> %s::vector) AS similarity
            FROM document_embeddings e
            WHERE e.tenant_id = %s
        """
        params: list[Any] = [embedding_str, tenant_id]

        if file_ids:
            sql += " AND e.document_id = ANY(%s)"
            params.append(file_ids)

        sql += " ORDER BY e.embedding <=> %s::vector LIMIT %s"
        params.extend([embedding_str, top_k * 2])  # fetch extra for threshold filter

        cur.execute(sql, params)
        rows = cur.fetchall()
        cur.close()

        results = []
        for r in rows:
            chunk_id, document_id, content, meta, score = r
            if threshold is not None and score < threshold:
                continue
            if len(results) >= top_k:
                break
            meta = meta or {}
            page = meta.get("chunk_index", 0) + 1 if isinstance(meta.get("chunk_index"), int) else 1
            results.append({
                "chunk_id": chunk_id,
                "file_id": document_id,
                "content": content or "",
                "page_number": page,
                "score": float(score),
                "provenance": {
                    "file_id": document_id,
                    "chunk_id": chunk_id,
                    "page": page,
                    "file_name": meta.get("file_name"),
                },
            })
        return results

    except Exception as e:
        logger.exception("semantic_search failed: %s", e)
        if conn:
            conn.rollback()
        return semantic_search_mock(query, tenant_id, project_id, top_k)


class PgVectorProvider:
    """Provider for pgvector semantic search. Falls back to mock on error."""

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
            query, tenant_id, project_id, top_k, file_ids, threshold
        )
        if threshold is not None and results:
            results = [r for r in results if r.get("score", 0) >= threshold]
        return results[:top_k]
