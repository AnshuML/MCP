"""ChromaDB provider - local vector DB, no PostgreSQL required.

Install: pip install chromadb
"""
from pathlib import Path
from typing import Any

from .mock_provider import semantic_search_mock

_chroma_client = None


def _get_chroma_client():
    """Lazy init ChromaDB client."""
    global _chroma_client
    if _chroma_client is not None:
        return _chroma_client
    try:
        import chromadb

        base = Path(__file__).resolve().parent.parent.parent.parent
        persist_dir = base / "data" / "chroma"
        persist_dir.mkdir(parents=True, exist_ok=True)
        client = chromadb.PersistentClient(path=str(persist_dir))
        _chroma_client = client
        return client
    except ImportError:
        return None


def _embed_query(query: str) -> list[float]:
    """Placeholder embedding. Replace with sentence-transformers or OpenAI."""
    return [0.0] * 384


class ChromaDBProvider:
    """
    ChromaDB provider - runs locally, no PostgreSQL.

    Expects collection "file_chunks" with metadata: tenant_id, project_id, file_id, chunk_id, page_number.
    Falls back to mock if ChromaDB not installed or query fails.
    """

    def semantic_search(
        self,
        query: str,
        tenant_id: str,
        project_id: str,
        top_k: int = 10,
        file_ids: list[str] | None = None,
        threshold: float | None = None,
    ) -> list[dict[str, Any]]:
        client = _get_chroma_client()
        if client is None:
            results = semantic_search_mock(query, tenant_id, project_id, top_k)
        else:
            try:
                coll = client.get_or_create_collection(
                    "file_chunks", metadata={"hnsw:space": "cosine"}
                )
                embedding = _embed_query(query)
                where = {"tenant_id": tenant_id, "project_id": project_id}
                res = coll.query(
                    query_embeddings=[embedding],
                    n_results=top_k,
                    where=where,
                    include=["documents", "metadatas", "distances"],
                )
                ids = res.get("ids", [[]])[0] if res else []
                if not ids:
                    results = semantic_search_mock(query, tenant_id, project_id, top_k)
                else:
                    results = []
                    metadatas = (res.get("metadatas") or [[]])[0]
                    documents = (res.get("documents") or [[]])[0]
                    distances = (res.get("distances") or [[]])[0]
                    for i, cid in enumerate(ids):
                        meta = metadatas[i] if i < len(metadatas) else {}
                        dist = distances[i] if i < len(distances) else 0.0
                        score = max(0, 1.0 - dist)
                        doc = documents[i] if i < len(documents) else ""
                        if file_ids and str(meta.get("file_id", "")) not in file_ids:
                            continue
                        results.append({
                            "chunk_id": str(meta.get("chunk_id", cid)),
                            "file_id": str(meta.get("file_id", "")),
                            "content": doc,
                            "page_number": int(meta.get("page_number", 1)),
                            "score": score,
                            "provenance": {
                                "file_id": meta.get("file_id"),
                                "chunk_id": meta.get("chunk_id", cid),
                                "page": meta.get("page_number", 1),
                            },
                        })
            except Exception:
                results = semantic_search_mock(query, tenant_id, project_id, top_k)

        if threshold is not None:
            results = [r for r in results if r.get("score", 0) >= threshold]
        return results
