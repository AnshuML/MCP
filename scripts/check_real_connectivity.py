"""Check if DB and Ollama are reachable for Phase 2 real-data testing."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import config


def check_db():
    """Test PostgreSQL connection."""
    print("\n[1] Checking PostgreSQL...")
    try:
        import psycopg2
        conn = psycopg2.connect(config.DATABASE_URL, connect_timeout=5)
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.fetchone()
        cur.execute(
            "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'document_metadata')"
        )
        has_table = cur.fetchone()[0]
        cur.close()
        conn.close()
        status = "document_metadata exists" if has_table else "connected, but document_metadata table not found"
        print(f"    OK - DB {status}.")
        return True
    except Exception as e:
        print(f"    FAIL - {e}")
        return False


def check_ollama():
    """Test Ollama embeddings API."""
    print("\n[2] Checking Ollama embeddings...")
    if not config.OLLAMA_URL:
        print("    FAIL - OLLAMA_URL not set")
        return False
    try:
        import urllib.request
        import json
        import base64

        url = f"{config.OLLAMA_URL}/api/embed"
        payload = {"model": config.OLLAMA_EMBEDDING_MODEL, "input": "test"}
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode(),
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        if config.OLLAMA_USERNAME and config.OLLAMA_PASSWORD:
            creds = base64.b64encode(
                f"{config.OLLAMA_USERNAME}:{config.OLLAMA_PASSWORD}".encode()
            ).decode()
            req.add_header("Authorization", f"Basic {creds}")

        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        emb = data.get("embedding") or (data.get("embeddings") or [[]])[0]
        if emb and len(emb) == config.EMBEDDING_DIM:
            print(f"    OK - Ollama returned {len(emb)}-dim embedding")
            return True
        print(f"    WARN - Unexpected dim {len(emb) if emb else 0}, expected {config.EMBEDDING_DIM}")
        return True  # still connected
    except Exception as e:
        print(f"    FAIL - {e}")
        return False


def main():
    print("Phase 2 - Real connectivity check")
    print("VECTOR_PROVIDER =", config.VECTOR_PROVIDER)
    db_ok = check_db()
    ollama_ok = check_ollama()
    print("\n" + "=" * 50)
    if db_ok and ollama_ok:
        print("All checks passed. Run: python scripts/test_tools.py")
        print("You should get REAL data (not mock).")
    else:
        print("Some checks failed. Fix connectivity, or use VECTOR_PROVIDER=mock for mock testing.")
        print("(DB needs VPN/K8s access; Ollama needs network reachability)")
    print("=" * 50)


if __name__ == "__main__":
    main()
