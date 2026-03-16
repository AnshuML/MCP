"""Document store - get_file_metadata and search_files.

Pluggable: PgDocumentStore (real DB) or MockDocumentStore (placeholder).
Schema: document_metadata, document_embeddings (Agent Swarm V2).
"""
import logging
from typing import Any, Protocol

from src.config import config

logger = logging.getLogger(__name__)

_store_instance: "DocumentStoreProtocol | None" = None


class DocumentStoreProtocol(Protocol):
    """Protocol for document metadata store."""

    def get_file_metadata(
        self, file_id: str, tenant_id: str, project_id: str
    ) -> dict[str, Any] | None:
        """Fetch metadata for a file. Returns None if not found."""
        ...

    def search_files(
        self,
        tenant_id: str,
        project_id: str,
        filters: dict[str, Any] | None,
        page: int,
        page_size: int,
    ) -> tuple[list[dict[str, Any]], int]:
        """Search files. Returns (files_list, total_count)."""
        ...


class MockDocumentStore:
    """Placeholder store - no DB, returns mock data."""

    def get_file_metadata(
        self, file_id: str, tenant_id: str, project_id: str
    ) -> dict[str, Any] | None:
        return {
            "file_id": file_id,
            "tenant_id": tenant_id,
            "project_id": project_id,
            "filename": "placeholder.txt",
            "mime_type": "text/plain",
            "size_bytes": 0,
            "processing_status": "pending",
            "upload_timestamp": None,
            "storage_uri": None,
        }

    def search_files(
        self,
        tenant_id: str,
        project_id: str,
        filters: dict[str, Any] | None,
        page: int,
        page_size: int,
    ) -> tuple[list[dict[str, Any]], int]:
        return [], 0


def _row_to_file_metadata(
    row: tuple, project_id: str
) -> dict[str, Any]:
    """Map document_metadata row to tool output format."""
    (
        document_id,
        tenant_id,
        file_name,
        document_type,
        chunk_count,
        created_at,
    ) = row
    return {
        "file_id": document_id,
        "tenant_id": tenant_id,
        "project_id": project_id,
        "filename": file_name or "unknown",
        "mime_type": document_type or "application/octet-stream",
        "size_bytes": None,
        "processing_status": "completed" if (chunk_count or 0) > 0 else "pending",
        "upload_timestamp": created_at.isoformat() if created_at else None,
        "storage_uri": None,
    }


class PgDocumentStore:
    """PostgreSQL document_metadata store. Tenant-isolated."""

    def __init__(self) -> None:
        self._conn = None

    def _get_conn(self):
        if self._conn is not None:
            try:
                self._conn.rollback()
                self._conn.cursor().execute("SELECT 1")
                return self._conn
            except Exception:
                self._conn = None
        try:
            import psycopg2

            self._conn = psycopg2.connect(config.DATABASE_URL)
            self._conn.autocommit = False
            return self._conn
        except Exception as e:
            logger.warning("DB connection failed: %s", e)
            return None

    def get_file_metadata(
        self, file_id: str, tenant_id: str, project_id: str
    ) -> dict[str, Any] | None:
        conn = self._get_conn()
        if not conn:
            return None
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT document_id, tenant_id, file_name, document_type,
                       chunk_count, created_at
                FROM document_metadata
                WHERE document_id = %s AND tenant_id = %s
                LIMIT 1
                """,
                (file_id, tenant_id),
            )
            row = cur.fetchone()
            cur.close()
            if not row:
                return None
            return _row_to_file_metadata(row, project_id)
        except Exception as e:
            logger.exception("get_file_metadata failed: %s", e)
            if conn:
                conn.rollback()
            return None

    def search_files(
        self,
        tenant_id: str,
        project_id: str,
        filters: dict[str, Any] | None,
        page: int,
        page_size: int,
    ) -> tuple[list[dict[str, Any]], int]:
        conn = self._get_conn()
        if not conn:
            return [], 0
        try:
            cur = conn.cursor()

            base_sql = """
                FROM document_metadata
                WHERE tenant_id = %s
            """
            params: list[Any] = [tenant_id]

            if filters:
                fname = filters.get("filename") or filters.get("file_name")
                if fname:
                    base_sql += " AND file_name ILIKE %s"
                    params.append(f"%{fname}%")
                if filters.get("mime_type") or filters.get("document_type"):
                    t = filters.get("document_type") or filters.get("mime_type")
                    base_sql += " AND document_type = %s"
                    params.append(t)
                if filters.get("processing_status"):
                    status = filters["processing_status"]
                    if status == "completed":
                        base_sql += " AND chunk_count > 0"
                    elif status == "pending":
                        base_sql += " AND (chunk_count IS NULL OR chunk_count = 0)"

            count_sql = "SELECT COUNT(*) " + base_sql
            cur.execute(count_sql, params)
            total = cur.fetchone()[0]

            order_sql = base_sql + " ORDER BY created_at DESC"
            data_sql = """
                SELECT document_id, tenant_id, file_name, document_type,
                       chunk_count, created_at
                """ + order_sql + " LIMIT %s OFFSET %s"
            params.extend([page_size, (page - 1) * page_size])
            cur.execute(data_sql, params)
            rows = cur.fetchall()
            cur.close()

            files = [_row_to_file_metadata(r, project_id) for r in rows]
            return files, total
        except Exception as e:
            logger.exception("search_files failed: %s", e)
            if conn:
                conn.rollback()
            return [], 0


def get_document_store() -> DocumentStoreProtocol:
    """Get document store based on VECTOR_PROVIDER (pgvector => real DB)."""
    global _store_instance
    if _store_instance is not None:
        return _store_instance

    provider = (config.VECTOR_PROVIDER or "").strip().lower()
    if not provider and config.PGVECTOR_ENABLED:
        provider = "pgvector"
    if not provider:
        provider = "mock"

    if provider == "pgvector":
        _store_instance = PgDocumentStore()
    else:
        _store_instance = MockDocumentStore()

    return _store_instance
