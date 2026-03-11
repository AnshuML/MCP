# Istedlal MCP Server – Complete Project Structure (File by File)

---

## Project Overview

**Istedlal MCP Server** – MCP (Model Context Protocol) server jo file metadata, search, aur semantic search tools expose karta hai. Clients (MCP Inspector, Cursor, custom apps) HTTP ya stdio se connect karte hain.

---

## Root Files

| File | Purpose |
|------|---------|
| **requirements.txt** | Python dependencies – mcp, python-dotenv, psycopg2, pgvector, pydantic |
| **Dockerfile** | Docker image – Python 3.12, pip install, `python -m src.main` |
| **.dockerignore** | Build se exclude – venv, .env, .cursor, __pycache__, docs, etc. |
| **.env** | Local config (env vars) – DB URL, tokens, transport – **commit mat karo** |
| **pyproject.toml** | Python project metadata (package name, etc.) |

---

## src/ – Main Application

### src/main.py

**Entry point** – server start, MCP setup, routes.

- **Transport security:** `enable_dns_rebinding_protection=False` – saare hosts allow (no "Invalid Host header")
- **Bearer auth:** Agar `MCP_BEARER_TOKEN` set hai to `/mcp` pe `Authorization: Bearer <token>` required
- **FastMCP:** MCP server instance – tools register, custom routes
- **Routes:** `GET /` (info JSON), `GET /favicon.ico` (204)
- **run():** `MCP_TRANSPORT` ke hisaab se stdio ya streamable-http start

---

## src/config/

### src/config/config.py

**Configuration** – `.env` se env vars load karta hai.

| Var | Default | Purpose |
|-----|---------|---------|
| MCP_TRANSPORT | stdio | stdio \| streamable-http |
| HTTP_HOST | 0.0.0.0 | Bind address |
| HTTP_PORT | 8000 | Port |
| DATABASE_URL | postgresql://... | PostgreSQL connection |
| PGVECTOR_ENABLED | false | pgvector use karein? |
| VECTOR_PROVIDER | mock | mock \| pgvector \| chromadb |
| LOG_LEVEL | INFO | Logging |
| MCP_BEARER_TOKEN | "" | Bearer tokens (comma-separated) |
| MCP_RESOURCE_SERVER_URL | https://localhost:8000/mcp | Auth metadata URL |

---

## src/auth/

### src/auth/static_bearer.py

**Bearer token verification** – `MCP_BEARER_TOKEN` se match karta hai.

- `StaticBearerTokenVerifier` – MCP SDK ka `TokenVerifier` implement
- Multiple tokens – comma-separated list, koi bhi valid ho to access
- `hmac.compare_digest` – constant-time comparison (timing attacks se bachne ke liye)

### src/auth/__init__.py

`StaticBearerTokenVerifier` export.

---

## src/tools/

### src/tools/__init__.py

**Tool registration** – saare tools ko FastMCP se register karta hai.

- `get_file_metadata` – file_id, tenant_id, project_id
- `search_files` – tenant_id, project_id, filters, page, page_size
- `semantic_search_files` – query, tenant_id, project_id, top_k, file_ids, threshold

### src/tools/get_file_metadata.py

**get_file_metadata tool** – file metadata return karta hai.

- Abhi mock data – Phase 2 mein DB se aayega
- Returns: file_id, filename, mime_type, size_bytes, processing_status, storage_uri, etc.

### src/tools/search_files.py

**search_files tool** – metadata filters se file search.

- Abhi mock – empty files list
- Phase 2: PostgreSQL provider se real search

### src/tools/semantic_search_files.py

**semantic_search_files tool** – natural language semantic search.

- `get_vector_provider()` se provider leta hai (mock/pgvector/chromadb)
- Provider ke `semantic_search()` ko call karta hai
- Returns: query, results (chunks with content, score, provenance), count

---

## src/providers/vector/

### src/providers/vector/base.py

**VectorProviderProtocol** – semantic search ka interface.

- `semantic_search(query, tenant_id, project_id, top_k, file_ids, threshold)` → list of dicts
- Naya provider add karne ke liye ye protocol implement karna hoga

### src/providers/vector/__init__.py

**Provider factory** – `VECTOR_PROVIDER` ke hisaab se provider choose karta hai.

- `get_vector_provider()` – singleton instance
- mock → MockVectorProvider
- pgvector → PgVectorProvider
- chromadb → ChromaDBProvider (ImportError pe mock fallback)

### src/providers/vector/mock_provider.py

**MockVectorProvider** – koi DB nahi, placeholder results.

- Har query pe 3 mock chunks return
- Dev/testing ke liye

### src/providers/vector/pgvector_provider.py

**PgVectorProvider** – PostgreSQL + pgvector extension.

- `chunks`, `files` tables expect karta hai
- Connection fail ho to mock fallback
- `_embed_query()` – abhi placeholder (384-dim zeros)

### src/providers/vector/chromadb_provider.py

**ChromaDBProvider** – ChromaDB (local vector DB).

- `data/chroma/` mein persist
- `file_chunks` collection – tenant_id, project_id metadata
- ChromaDB install nahi hai to mock fallback

---

## .cursor/mcp.json

**Cursor MCP config** – Cursor IDE MCP server kaise start kare.

- Command: `venv\python.exe -m src.main`
- env: `MCP_TRANSPORT=stdio`
- Cursor stdio se connect karta hai

---

## scripts/

### scripts/test_tools.py

**Tool tests** – `get_file_metadata`, `search_files`, `semantic_search_files` ko direct call karke verify karta hai.

---

## docs/

| File | Purpose |
|------|---------|
| **README.md** | Setup, run, tools, production section |
| **ENV_SETUP.md** | Env variables, Supabase/Neon, Bearer auth |
| **VECTOR_PROVIDERS.md** | mock, pgvector, chromadb – kaise use karein |
| **PRODUCTION_HANDOVER.md** | Deployment team ke liye checklist |
| **MCP_INSPECTOR_GUIDE.md** | MCP Inspector se test karne ka guide |
| **POSTGRES_LOCAL_SETUP.md** | Local PostgreSQL setup |
| **PROGRESS_REPORT_2025-03-08.md** | Phase 1 progress |
| **DAILY_SUMMARY_2025-03-10.md** | 10 March ka summary |

---

## Data Flow

```
Client (Inspector/Cursor)
    ↓ HTTP / stdio
src/main.py (FastMCP)
    ↓ tool call
src/tools/__init__.py (registered tools)
    ↓ e.g. semantic_search_files
src/tools/semantic_search_files.py
    ↓ get_vector_provider()
src/providers/vector/__init__.py (factory)
    ↓ MockVectorProvider / PgVectorProvider / ChromaDBProvider
Provider.semantic_search()
    ↓ results
Response → Client
```

---

## Quick Reference

| Run locally | `python -m src.main` |
| Test tools | `python scripts/test_tools.py` |
| MCP Inspector | `npx -y @modelcontextprotocol/inspector` |
| Root URL | `http://localhost:8000/` |
| MCP endpoint | `http://localhost:8000/mcp` |
