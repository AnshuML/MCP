"""Ollama embedding client for semantic search.

Calls Ollama /api/embed with Basic Auth. Enterprise-grade: timeout, logging.
"""
import base64
import logging
from typing import Any

from src.config import config

logger = logging.getLogger(__name__)

_EMBEDDING_CACHE: dict[str, list[float]] = {}


def get_query_embedding(query: str) -> list[float] | None:
    """
    Get embedding vector for a search query via Ollama API.

    Returns:
        List of floats (3072 dims for llama3.2) or None on failure.
    """
    if not query or not query.strip():
        logger.warning("get_query_embedding called with empty query")
        return None

    if not config.OLLAMA_URL:
        logger.debug("OLLAMA_URL not set, embedding unavailable")
        return None

    # Simple cache to avoid repeat calls for identical queries (optional, small cache)
    cache_key = query.strip()[:500]
    if cache_key in _EMBEDDING_CACHE:
        return _EMBEDDING_CACHE[cache_key]

    try:
        import urllib.error
        import urllib.request

        import json

        url = f"{config.OLLAMA_URL}/api/embed"
        payload = {"model": config.OLLAMA_EMBEDDING_MODEL, "input": query.strip()[:2000]}

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            method="POST",
            headers={"Content-Type": "application/json"},
        )

        if config.OLLAMA_USERNAME and config.OLLAMA_PASSWORD:
            credentials = base64.b64encode(
                f"{config.OLLAMA_USERNAME}:{config.OLLAMA_PASSWORD}".encode()
            ).decode()
            req.add_header("Authorization", f"Basic {credentials}")

        with urllib.request.urlopen(req, timeout=config.OLLAMA_TIMEOUT_SEC) as resp:
            data: dict[str, Any] = json.loads(resp.read().decode())

        # Ollama returns "embedding" (single) or "embeddings" (array)
        embedding = data.get("embedding") or (
            data.get("embeddings", [[]])[0] if data.get("embeddings") else None
        )
        if not isinstance(embedding, list) or not embedding:
            logger.error("Ollama returned invalid embedding format")
            return None

        vec = [float(x) for x in embedding]
        if len(vec) != config.EMBEDDING_DIM:
            logger.warning(
                "Embedding dim %s != expected %s", len(vec), config.EMBEDDING_DIM
            )

        # Cache for repeated queries
        if len(_EMBEDDING_CACHE) < 100:
            _EMBEDDING_CACHE[cache_key] = vec

        return vec

    except Exception as e:
        logger.exception("Ollama embedding request failed: %s", e)
        return None
