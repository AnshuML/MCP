"""Mock vector provider - no DB required, returns placeholder results."""
from typing import Any


def semantic_search_mock(
    query: str,
    tenant_id: str,
    project_id: str,
    top_k: int = 10,
) -> list[dict[str, Any]]:
    """Mock semantic search - returns placeholder results for testing."""
    return [
        {
            "chunk_id": f"chunk-{i}",
            "file_id": "file-mock-001",
            "content": f"Sample content for query '{query[:30]}...' (mock result {i})",
            "page_number": i + 1,
            "score": 0.95 - (i * 0.05),
            "provenance": {
                "file_id": "file-mock-001",
                "chunk_id": f"chunk-{i}",
                "page": i + 1,
                "workflow_version": "1.0",
                "extractor": "mock",
            },
        }
        for i in range(min(top_k, 3))
    ]


class MockVectorProvider:
    """Mock provider - always works, no external dependencies."""

    def semantic_search(
        self,
        query: str,
        tenant_id: str,
        project_id: str,
        top_k: int = 10,
        file_ids: list[str] | None = None,
        threshold: float | None = None,
    ) -> list[dict[str, Any]]:
        results = semantic_search_mock(query, tenant_id, project_id, top_k)
        if threshold is not None:
            results = [r for r in results if r.get("score", 0) >= threshold]
        return results
