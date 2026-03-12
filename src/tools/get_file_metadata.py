"""get_file_metadata tool - Fetch metadata for a file by ID."""
from typing import Any

from src.db import get_document_store


def get_file_metadata(file_id: str, tenant_id: str, project_id: str) -> dict[str, Any]:
    """
    Fetch metadata for a specific file.

    Args:
        file_id: Unique identifier (document_id in DB)
        tenant_id: Tenant context for authorization
        project_id: Project context (passed through; not in schema)

    Returns:
        File metadata or placeholder when store unavailable.
    """
    store = get_document_store()
    result = store.get_file_metadata(file_id, tenant_id, project_id)
    if result is not None:
        return result
    # Not found or store unavailable
    return {
        "file_id": file_id,
        "tenant_id": tenant_id,
        "project_id": project_id,
        "filename": None,
        "mime_type": None,
        "size_bytes": None,
        "processing_status": "not_found",
        "upload_timestamp": None,
        "storage_uri": None,
    }
