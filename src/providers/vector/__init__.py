"""Vector search providers - pluggable backends (mock, pgvector, chromadb)."""
from typing import TYPE_CHECKING

from src.config import config

from .base import VectorProviderProtocol
from .mock_provider import MockVectorProvider
from .pgvector_provider import PgVectorProvider

if TYPE_CHECKING:
    pass

_provider_instance = None


def get_vector_provider() -> VectorProviderProtocol:
    """Get vector provider based on VECTOR_PROVIDER config."""
    global _provider_instance
    if _provider_instance is not None:
        return _provider_instance

    provider_name = (config.VECTOR_PROVIDER or "").strip().lower()
    if not provider_name and config.PGVECTOR_ENABLED:
        provider_name = "pgvector"
    if not provider_name:
        provider_name = "mock"

    if provider_name == "pgvector":
        _provider_instance = PgVectorProvider()
    elif provider_name == "chromadb":
        try:
            from .chromadb_provider import ChromaDBProvider

            _provider_instance = ChromaDBProvider()
        except ImportError:
            _provider_instance = MockVectorProvider()
    else:
        _provider_instance = MockVectorProvider()

    return _provider_instance


__all__ = [
    "VectorProviderProtocol",
    "MockVectorProvider",
    "PgVectorProvider",
    "get_vector_provider",
]
