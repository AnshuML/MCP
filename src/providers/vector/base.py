"""Abstract interface for vector search providers.

Use this to plug in any backend: pgvector, ChromaDB, Pinecone, Qdrant, etc.
"""
from typing import Any, Protocol


class VectorProviderProtocol(Protocol):
    """Protocol for semantic search over file embeddings."""

    def semantic_search(
        self,
        query: str,
        tenant_id: str,
        project_id: str,
        top_k: int = 10,
        file_ids: list[str] | None = None,
        threshold: float | None = None,
    ) -> list[dict[str, Any]]:
        """
        Run semantic search.

        Returns list of dicts with: chunk_id, file_id, content, page_number, score, provenance.
        """
        ...
