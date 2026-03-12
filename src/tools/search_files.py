"""search_files tool - Search files using metadata filters."""
from typing import Any

from src.db import get_document_store


def search_files(
    tenant_id: str,
    project_id: str,
    filters: dict[str, Any] | None = None,
    page: int = 1,
    page_size: int = 20,
) -> dict[str, Any]:
    """
    Search files using metadata filters.

    Args:
        tenant_id: Tenant context
        project_id: Project context (passed through)
        filters: Optional - filename, mime_type/document_type, processing_status
        page: Page number (1-based)
        page_size: Results per page

    Returns:
        files, total_count, page, page_size, has_more
    """
    page = max(1, page)
    page_size = min(max(1, page_size), 100)

    store = get_document_store()
    files, total_count = store.search_files(
        tenant_id=tenant_id,
        project_id=project_id,
        filters=filters,
        page=page,
        page_size=page_size,
    )
    return {
        "files": files,
        "total_count": total_count,
        "page": page,
        "page_size": page_size,
        "has_more": (page * page_size) < total_count,
    }
