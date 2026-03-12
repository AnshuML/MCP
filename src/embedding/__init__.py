"""Embedding providers for semantic search."""
from .ollama_client import get_query_embedding

__all__ = ["get_query_embedding"]
