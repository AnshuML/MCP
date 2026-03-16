"""Integration tests for all MCP tools (built-in + external API)."""
import sys
from pathlib import Path

import pytest

# Project root
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


# --- Built-in tools ---
def test_get_file_metadata():
    from src.tools.get_file_metadata import get_file_metadata

    result = get_file_metadata(
        file_id="test-file-001",
        tenant_id="tenant-1",
        project_id="project-1",
    )
    assert isinstance(result, dict), "get_file_metadata must return dict"
    assert "file_id" in result and "tenant_id" in result
    assert result["file_id"] == "test-file-001"


def test_search_files():
    from src.tools.search_files import search_files

    result = search_files(
        tenant_id="tenant-1",
        project_id="project-1",
        filters={"processing_status": "completed"},
        page=1,
        page_size=10,
    )
    assert isinstance(result, dict)
    assert "files" in result and "total_count" in result
    assert "page" in result and "page_size" in result and "has_more" in result
    assert isinstance(result["files"], list)


def test_semantic_search_files():
    from src.tools.semantic_search_files import semantic_search_files

    result = semantic_search_files(
        query="What is the weather report?",
        tenant_id="tenant-1",
        project_id="project-1",
        top_k=5,
    )
    assert isinstance(result, dict)
    assert "query" in result and "results" in result and "count" in result
    assert isinstance(result["results"], list)
    assert result["query"] == "What is the weather report?"


# --- External API loader ---
def test_external_api_load_config():
    from src.external_api.loader import load_config

    apis = load_config()
    assert isinstance(apis, list)


# --- External API client (live GET; skip if no network) ---
def test_external_api_call_api():
    from src.external_api.client import call_api

    result = call_api(
        base_url="https://httpbin.org",
        path="/get",
        method="GET",
        params={"test": "mcp"},
        auth="none",
        timeout_sec=15,
    )
    assert isinstance(result, dict)
    assert "success" in result
    if result["success"]:
        assert "data" in result
    else:
        # Network unreachable etc. - still valid response shape
        assert "error" in result


# --- External API registration (no exception) ---
def test_external_api_registration():
    from mcp.server.fastmcp import FastMCP

    from src.external_api import register_external_api_tools
    from src.tools import register_tools

    mcp = FastMCP("test")
    register_tools(mcp)
    register_external_api_tools(mcp)  # must not raise
