"""semantic_search_files tool - Semantic search over file embeddings (pgvector)."""
from typing import Any

from src.providers.vector import get_vector_provider


def semantic_search_files(
    query: str,
    tenant_id: str,
    project_id: str,
    top_k: int = 10,
    file_ids: list[str] | None = None,
    threshold: float | None = None,
) -> dict[str, Any]:
    """
    Perform semantic search over file embeddings stored in pgvector.

    Args:
        query: Natural language search query
        tenant_id: Tenant context for authorization
        project_id: Project context for authorization
        top_k: Maximum number of results to return (default 10)
        file_ids: Optional filter to search only within specific files
        threshold: Optional minimum similarity score (0-1)

    Returns:
        Ranked chunk results with content, scores, and provenance
    """
    provider = get_vector_provider()
    results = provider.semantic_search(
        query=query,
        tenant_id=tenant_id,
        project_id=project_id,
        top_k=top_k,
        file_ids=file_ids,
        threshold=threshold,
    )
    return {
        "query": query,
        "results": results,
        "count": len(results),
    }
