"""MCP Tools registration."""
from mcp.server.fastmcp import FastMCP

from .get_file_metadata import get_file_metadata
from .search_files import search_files
from .semantic_search_files import semantic_search_files


def register_tools(mcp: FastMCP) -> None:
    """Register all MCP tools with the server."""

    @mcp.tool(name="get_file_metadata")
    def get_file_metadata_tool(
        file_id: str,
        tenant_id: str,
        project_id: str,
    ) -> dict:
        """Fetch metadata for a specific file by ID. Returns file details including filename, mime_type, size, processing_status, and storage info."""
        return get_file_metadata(file_id, tenant_id, project_id)

    @mcp.tool(name="search_files")
    def search_files_tool(
        tenant_id: str,
        project_id: str,
        filters: dict | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """Search files using metadata filters. Supports filters like filename, mime_type, processing_status, upload date range."""
        return search_files(tenant_id, project_id, filters, page, page_size)

    @mcp.tool(name="semantic_search_files")
    def semantic_search_files_tool(
        query: str,
        tenant_id: str,
        project_id: str,
        top_k: int = 10,
        file_ids: list[str] | None = None,
        threshold: float | None = None,
    ) -> dict:
        """Semantic search over file embeddings. Use natural language to find relevant content across files."""
        return semantic_search_files(
            query, tenant_id, project_id, top_k, file_ids, threshold
        )
