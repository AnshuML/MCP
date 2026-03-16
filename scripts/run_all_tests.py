"""
Run all MCP tool tests: built-in tools + external API (loader, client, registration).
Exit 0 = all passed, 1 = any failed.
"""
import json
import os
import sys
from pathlib import Path

# Project root
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

FAILED = []
PASSED = []


def ok(name: str) -> None:
    PASSED.append(name)
    print(f"  [OK] {name}")


def fail(name: str, msg: str) -> None:
    FAILED.append((name, msg))
    print(f"  [FAIL] {name}: {msg}")


# --- Built-in tools ---
def test_get_file_metadata() -> None:
    from src.tools.get_file_metadata import get_file_metadata

    result = get_file_metadata(
        file_id="test-file-001",
        tenant_id="tenant-1",
        project_id="project-1",
    )
    if not isinstance(result, dict):
        fail("get_file_metadata", f"expected dict, got {type(result)}")
        return
    if "file_id" not in result or "tenant_id" not in result:
        fail("get_file_metadata", "missing file_id or tenant_id in result")
        return
    ok("get_file_metadata")


def test_search_files() -> None:
    from src.tools.search_files import search_files

    result = search_files(
        tenant_id="tenant-1",
        project_id="project-1",
        filters={"processing_status": "completed"},
        page=1,
        page_size=10,
    )
    if not isinstance(result, dict):
        fail("search_files", f"expected dict, got {type(result)}")
        return
    for key in ("files", "total_count", "page", "page_size", "has_more"):
        if key not in result:
            fail("search_files", f"missing key: {key}")
            return
    if not isinstance(result["files"], list):
        fail("search_files", "files must be list")
        return
    ok("search_files")


def test_semantic_search_files() -> None:
    from src.tools.semantic_search_files import semantic_search_files

    result = semantic_search_files(
        query="What is the weather report?",
        tenant_id="tenant-1",
        project_id="project-1",
        top_k=5,
    )
    if not isinstance(result, dict):
        fail("semantic_search_files", f"expected dict, got {type(result)}")
        return
    if "query" not in result or "results" not in result or "count" not in result:
        fail("semantic_search_files", "missing query/results/count")
        return
    if not isinstance(result["results"], list):
        fail("semantic_search_files", "results must be list")
        return
    ok("semantic_search_files")


# --- External API: config loader ---
def test_external_api_loader() -> None:
    from src.external_api.loader import load_config

    apis = load_config()
    if not isinstance(apis, list):
        fail("external_api.load_config", f"expected list, got {type(apis)}")
        return
    ok("external_api.load_config")


# --- External API: fake credentials -> tool works (httpbin as fake API) ---
def test_external_api_tool_with_fake_credentials() -> None:
    """Set fake API URL (httpbin), load config, call that endpoint - proves full flow works."""
    os.environ["TEST_ECHO_API_URL"] = "https://httpbin.org"
    try:
        from src.external_api.loader import load_config
        from src.external_api.client import call_api

        apis = load_config()
        test_api = next((a for a in apis if a.get("id") == "test_echo"), None)
        if not test_api:
            fail("external_api.fake_credentials", "test_echo API not loaded (set TEST_ECHO_API_URL)")
            return
        base_url = test_api.get("base_url", "")
        endpoints = test_api.get("endpoints") or []
        ep = next((e for e in endpoints if e.get("tool_name") == "test_echo_get"), None)
        if not ep:
            fail("external_api.fake_credentials", "test_echo_get endpoint not found")
            return
        result = call_api(
            base_url=base_url,
            path=ep.get("path", "/get"),
            method=ep.get("method", "GET"),
            params={"test_key": "mcp_verify"},
            auth="none",
            timeout_sec=15,
        )
        if not result.get("success"):
            fail("external_api.fake_credentials", result.get("error", "call failed"))
            return
        if "data" not in result:
            fail("external_api.fake_credentials", "missing data in response")
            return
        ok("external_api.fake_credentials (tool works with fake API)")
    finally:
        os.environ.pop("TEST_ECHO_API_URL", None)


# --- External API: client (live GET to public API; valid shape even if network fails) ---
def test_external_api_client() -> None:
    from src.external_api.client import call_api

    result = call_api(
        base_url="https://httpbin.org",
        path="/get",
        method="GET",
        params={"test": "mcp"},
        auth="none",
        timeout_sec=15,
    )
    if not isinstance(result, dict):
        fail("external_api.call_api", f"expected dict, got {type(result)}")
        return
    if "success" not in result:
        fail("external_api.call_api", "missing 'success' in result")
        return
    if result["success"]:
        if "data" not in result:
            fail("external_api.call_api", "missing 'data' when success=True")
            return
    else:
        if "error" not in result:
            fail("external_api.call_api", "missing 'error' when success=False")
            return
    ok("external_api.call_api")


# --- External API: registration (with fake URL so test_echo tool is registered) ---
def test_external_api_registration() -> None:
    os.environ["TEST_ECHO_API_URL"] = "https://httpbin.org"
    try:
        from mcp.server.fastmcp import FastMCP
        from src.tools import register_tools
        from src.external_api import register_external_api_tools

        mcp = FastMCP("test")
        register_tools(mcp)
        register_external_api_tools(mcp)
        ok("external_api.register_external_api_tools")
    except Exception as e:
        fail("external_api.register_external_api_tools", str(e))
    finally:
        os.environ.pop("TEST_ECHO_API_URL", None)


# --- Main ---
def main() -> int:
    print("\n" + "=" * 60)
    print("Istedlal MCP – Full test run (all tools + external API)")
    print("=" * 60)

    print("\n--- Built-in tools ---")
    test_get_file_metadata()
    test_search_files()
    test_semantic_search_files()

    print("\n--- External API (Phase 3) ---")
    test_external_api_loader()
    test_external_api_client()
    test_external_api_tool_with_fake_credentials()  # fake credential -> tool works
    test_external_api_registration()

    print("\n" + "=" * 60)
    if FAILED:
        print(f"FAILED: {len(FAILED)}")
        for name, msg in FAILED:
            print(f"  - {name}: {msg}")
        print(f"PASSED: {len(PASSED)}")
        print("=" * 60 + "\n")
        return 1
    print(f"All {len(PASSED)} tests passed.")
    print("=" * 60 + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
