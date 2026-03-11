"""search_files tool - Search files using metadata filters."""
from typing import Any


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
        project_id: Project context
        filters: Optional filters (filename, mime_type, processing_status, etc.)
        page: Page number for pagination
        page_size: Number of results per page

    Returns:
        List of file summaries and pagination info (placeholder)
    """
    # Phase 1: Mock response. Phase 2: Query via PostgreSQL provider.
    return {
        "files": [],
        "total_count": 0,
        "page": page,
        "page_size": page_size,
        "has_more": False,
    }
