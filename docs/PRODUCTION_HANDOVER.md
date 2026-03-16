# Production Deployment – Handover for Deployment Team

## What to Deploy

**Istedlal MCP Server** – MCP (Model Context Protocol) server exposing tools for file metadata, search, and semantic search. Clients (MCP Inspector, Cursor, custom apps) connect via HTTP.

---

## Required Environment Variables (Server)

| Variable | Required | Example |
|----------|----------|---------|
| `MCP_TRANSPORT` | Yes | `streamable-http` |
| `MCP_HTTP_STREAMS_ENABLED` | No | `true` to enable HTTP streams (connection open, chunked data). Default `false`. |
| `MCP_BEARER_TOKEN` | **Yes** | `token1,token2,token3` (comma-separated; any one grants access) |
| `VECTOR_PROVIDER` | No | `mock` \| `pgvector` \| `chromadb` (default: mock) |
| `DATABASE_URL` | If VECTOR_PROVIDER=pgvector | `postgresql://user:pass@host:5432/dbname` |
| `PGVECTOR_ENABLED` | No | `true` when using pgvector |
| `OLLAMA_URL` | If semantic search | Ollama base URL (e.g. https://gpu1.oginnovation.com:11433) |
| `OLLAMA_EMBEDDING_MODEL` | No | llama3.2 (must match DB) |
| `OLLAMA_USERNAME` / `OLLAMA_PASSWORD` | If auth | Basic Auth for Ollama |
| `HTTP_HOST` | No | `0.0.0.0` |
| `HTTP_PORT` | No | `8000` |
| `LOG_LEVEL` | No | `INFO` |

**Important:** `MCP_BEARER_TOKEN` must be set in production. Use strong, unique tokens. No quotes in `.env` – write `100` not `"100"`.

### HTTP Streams Mode (Deployment Team Request)

When `MCP_HTTP_STREAMS_ENABLED=true`:
- HTTP connection **stays open** instead of closing after each response
- Data is sent in **small chunks** over time (Server-Sent Events)
- Better for large data, real-time updates, long-running tasks
- Reduces memory usage on client and server

Set in `.env`: `MCP_HTTP_STREAMS_ENABLED=true`

---

## What Clients Need

- **URL:** `http://<your-server-hostname>:8000/mcp`
- **Auth:** Every request must include header: `Authorization: Bearer <valid-token>`
- Valid token = any one from the comma-separated `MCP_BEARER_TOKEN` list

---

## Docker (if using)

```bash
docker build -t istedlal-mcp .
docker run -p 8000:8000 \
  -e MCP_BEARER_TOKEN=token1,token2 \
  -e DATABASE_URL=postgresql://... \
  istedlal-mcp
```

---

## Verify

1. **Health:** `curl http://localhost:8000/` → JSON with `status: running`
2. **MCP endpoint:** `/mcp` (for MCP clients only; needs Bearer token)

---

## Phase 1 – Known Issues & Fixes (Production Person)

Agar client "Could not connect" / "Could not load list" / errors dikhayi de, to yeh check karein:

| Issue | Cause | Fix |
|-------|-------|-----|
| **Invalid Host header (421)** | Host allowlist block | Fixed in code – all hosts allowed. No action needed. |
| **invalid_token / 401** | Bearer token missing/wrong | Client ko `Authorization: Bearer <token>` bhejna hoga. Token `.env` ke `MCP_BEARER_TOKEN` se match hona chahiye. |
| **Protected resource https vs http** | MCP_RESOURCE_SERVER_URL galat | `.env` mein `MCP_RESOURCE_SERVER_URL=http://your-actual-url:8000/mcp` set karein (http, not https, unless SSL hai). |
| **400 Bad Request / Missing session ID** | Session flow issue | Fixed – `stateless_http=True`. No action needed. |
| **Could not connect (n8n / MCP Inspector)** | Network / URL | n8n Docker mein ho to `http://host.docker.internal:8000/mcp` use karein. K8s mein ho to service URL: `http://mcp-server-backend-service.<namespace>.svc.cluster.local:8000/mcp` |
| **Tool list load nahi hota** | Connection fail | Pehle `curl http://<server>:8000/` se health check. Server reachable hona chahiye. |
| **406 Not Acceptable** | Client Accept header missing/wrong | Client **must** send `Accept: application/json` (and `text/event-stream` for SSE mode). n8n / MCP Inspector usually send this – check client config. |

### Client URL Reference

| Client Location | MCP URL (example) |
|-----------------|-------------------|
| Same machine (host) | `http://localhost:8000/mcp` |
| n8n in Docker | `http://host.docker.internal:8000/mcp` |
| K8s – same namespace | `http://mcp-server-backend-service:8000/mcp` |
| K8s – different namespace | `http://mcp-server-backend-service.<namespace>.svc.cluster.local:8000/mcp` |

---

## Phase 2 – Real DB Integration

**Schema (Agent Swarm V2):** `document_metadata`, `document_embeddings` in PostgreSQL + pgvector.

**To enable:**
1. Set `VECTOR_PROVIDER=pgvector`
2. Set `DATABASE_URL` to reachable PostgreSQL
3. Set `OLLAMA_URL` for semantic search (query embeddings)
4. Tables must exist: `document_metadata`, `document_embeddings` (see `data/vectordb_schema_documentation.pdf`)

**Tenant isolation:** All queries filter by `tenant_id`. No `project_id` in schema.

---

## Phase 3 – External APIs (Config-Only)

External APIs are exposed as MCP tools **without code changes**.

- **Config:** `config/apis.yaml` – add new API blocks with `base_url_env`, `auth`, `endpoints` (path, method, tool_name, params).
- **Credentials:** In `.env` set the env vars referenced in config (e.g. `DOCCONTEXT_API_URL`, optional `DOCCONTEXT_API_TOKEN`).
- APIs whose base URL env is not set are skipped at startup. Restart server after config/env changes.

See `docs/ENV_SETUP.md` → External APIs (Phase 3) and `config/apis.yaml` comments.

---

## Reference Docs

- `docs/ENV_SETUP.md` – Full env variable details
- `README.md` – Setup and run instructions
