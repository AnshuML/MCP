"""Test get_file_metadata and search_files tools."""
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools.get_file_metadata import get_file_metadata
from src.tools.search_files import search_files
from src.tools.semantic_search_files import semantic_search_files


def test_get_file_metadata():
    """Test get_file_metadata tool."""
    print("\n" + "=" * 50)
    print("Testing: get_file_metadata")
    print("=" * 50)
    
    result = get_file_metadata(
        file_id="test-file-001",
        tenant_id="tenant-1",
        project_id="project-1",
    )
    
    print(json.dumps(result, indent=2))
    print("\n[OK] get_file_metadata passed\n")


def test_semantic_search_files():
    """Test semantic_search_files tool (Phase 2 - pgvector)."""
    print("=" * 50)
    print("Testing: semantic_search_files")
    print("=" * 50)

    result = semantic_search_files(
        query="What is the weather report?",
        tenant_id="tenant-1",
        project_id="project-1",
        top_k=5,
    )

    print(json.dumps(result, indent=2))
    print("\n[OK] semantic_search_files passed\n")


def test_search_files():
    """Test search_files tool."""
    print("=" * 50)
    print("Testing: search_files")
    print("=" * 50)
    
    result = search_files(
        tenant_id="tenant-1",
        project_id="project-1",
        filters={"processing_status": "completed"},
        page=1,
        page_size=10,
    )
    
    print(json.dumps(result, indent=2))
    print("\n[OK] search_files passed\n")


if __name__ == "__main__":
    print("\nIstedlal MCP - Tool Tests\n")
    test_get_file_metadata()
    test_search_files()
    test_semantic_search_files()
    print("=" * 50)
    print("All tests completed!")
    print("=" * 50)
