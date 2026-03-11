"""Configuration loader for MCP Server."""
import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root
_env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(_env_path)


class Config:
    """Application configuration from environment."""

    # Server
    MCP_TRANSPORT: str = os.getenv("MCP_TRANSPORT", "stdio")  # stdio | streamable-http
    HTTP_HOST: str = os.getenv("HTTP_HOST", "0.0.0.0")
    HTTP_PORT: int = int(os.getenv("HTTP_PORT", "8000"))

    # Database (for Phase 2+)
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:pass@localhost:5432/istedlal",
    )
    PGVECTOR_ENABLED: bool = os.getenv("PGVECTOR_ENABLED", "false").lower() == "true"

    # Vector provider: mock | pgvector | chromadb
    # mock = no DB (placeholder results)
    # pgvector = PostgreSQL + pgvector extension
    # chromadb = ChromaDB (local, no PostgreSQL)
    VECTOR_PROVIDER: str = os.getenv("VECTOR_PROVIDER", "mock")

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


    # Bearer token auth (optional) - comma-separated list; any valid token grants access
    MCP_BEARER_TOKEN: str = os.getenv("MCP_BEARER_TOKEN", "")

    # Resource server URL for auth metadata (only used when MCP_BEARER_TOKEN is set)
    MCP_RESOURCE_SERVER_URL: str = os.getenv("MCP_RESOURCE_SERVER_URL", "https://localhost:8000/mcp")


config = Config()
