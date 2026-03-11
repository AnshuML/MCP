# Production Deployment – Handover for Deployment Team

## What to Deploy

**Istedlal MCP Server** – MCP (Model Context Protocol) server exposing tools for file metadata, search, and semantic search. Clients (MCP Inspector, Cursor, custom apps) connect via HTTP.

---

## Required Environment Variables (Server)

| Variable | Required | Example |
|----------|----------|---------|
| `MCP_TRANSPORT` | Yes | `streamable-http` |
| `MCP_BEARER_TOKEN` | **Yes** | `token1,token2,token3` (comma-separated; any one grants access) |
| `VECTOR_PROVIDER` | No | `mock` \| `pgvector` \| `chromadb` (default: mock) |
| `DATABASE_URL` | If VECTOR_PROVIDER=pgvector | `postgresql://user:pass@host:5432/dbname` |
| `PGVECTOR_ENABLED` | No | `true` when using pgvector |
| `HTTP_HOST` | No | `0.0.0.0` |
| `HTTP_PORT` | No | `8000` |
| `LOG_LEVEL` | No | `INFO` |

**Important:** `MCP_BEARER_TOKEN` must be set in production. Use strong, unique tokens. No quotes in `.env` – write `100` not `"100"`.

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

### Client URL Reference

| Client Location | MCP URL (example) |
|-----------------|-------------------|
| Same machine (host) | `http://localhost:8000/mcp` |
| n8n in Docker | `http://host.docker.internal:8000/mcp` |
| K8s – same namespace | `http://mcp-server-backend-service:8000/mcp` |
| K8s – different namespace | `http://mcp-server-backend-service.<namespace>.svc.cluster.local:8000/mcp` |

---

## Reference Docs

- `docs/ENV_SETUP.md` – Full env variable details
- `README.md` – Setup and run instructions
