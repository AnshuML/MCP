# Environment Variables Setup

## Quick Setup

1. Create `.env` in project root with your values (see table below)
2. App loads vars automatically via `python-dotenv`

---

## Remote PostgreSQL (Supabase / Neon)

### Supabase
1. Create project at [supabase.com](https://supabase.com)
2. Go to **Settings → Database** for connection string
3. In `.env`:
```
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.xxxxxxxx.supabase.co:5432/postgres
PGVECTOR_ENABLED=true
```

### Neon
1. Create project at [neon.tech](https://neon.tech)
2. Copy connection string from dashboard
3. In `.env`:
```
DATABASE_URL=postgresql://user:pass@ep-xxx.region.aws.neon.tech/neondb?sslmode=require
PGVECTOR_ENABLED=true
```

---

## Production Deployment

**All hosts are allowed.** Security is enforced via **Bearer token authentication** instead of host allowlisting.

### Bearer Token Auth (Recommended for Production)

1. Set `MCP_BEARER_TOKEN` in your server `.env` (single or comma-separated):
   ```
   MCP_BEARER_TOKEN=your-secret-token-here
   # Or multiple: MCP_BEARER_TOKEN=token1,token2,token3
   ```

2. Clients must send the token in every request:
   ```
   Authorization: Bearer your-secret-token-here
   ```

3. MCP Inspector / Test Client: use the auth/header field to add the Bearer token.

4. Optional: Set `MCP_RESOURCE_SERVER_URL` to your public MCP URL (for `WWW-Authenticate` header):
   ```
   MCP_RESOURCE_SERVER_URL=https://mcp.yourdomain.com/mcp
   ```

---

## All Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| MCP_TRANSPORT | No | `stdio` (IDE) or `streamable-http` (Inspector/HTTP) | streamable-http |
| HTTP_HOST | No | Bind address (default: 0.0.0.0) | 0.0.0.0 |
| HTTP_PORT | No | HTTP port (default: 8000) | 8000 |
| DATABASE_URL | Yes* | PostgreSQL connection string | postgresql://user:pass@host:5432/db |
| PGVECTOR_ENABLED | No | `true` = use pgvector (when VECTOR_PROVIDER=pgvector) | false |
| VECTOR_PROVIDER | No | `mock` \| `pgvector` \| `chromadb` – see [VECTOR_PROVIDERS.md](VECTOR_PROVIDERS.md) | mock |
| LOG_LEVEL | No | Logging level | INFO |
| MCP_BEARER_TOKEN | **Yes (Production)** | Comma-separated tokens; any valid token grants access | token1,token2,token3 |
| MCP_RESOURCE_SERVER_URL | No | Public MCP URL for auth metadata (when using Bearer token) | https://mcp.example.com/mcp |
| MCP_HTTP_STREAMS_ENABLED | No | `true` = HTTP streams (connection open, chunked data). Default `false`. | false |
| OLLAMA_URL | Phase 2 | Ollama base URL for embeddings (e.g. https://gpu1.oginnovation.com:11433) | (empty) |
| OLLAMA_EMBEDDING_MODEL | Phase 2 | Model name (must match DB embedding dim) | llama3.2 |
| OLLAMA_USERNAME | Phase 2 | Basic Auth username (if required) | (empty) |
| OLLAMA_PASSWORD | Phase 2 | Basic Auth password | (empty) |
| EMBEDDING_DIM | Phase 2 | Vector dimension (3072 for llama3.2) | 3072 |
| **External APIs (Phase 3)** | | | |
| APIS_CONFIG_PATH | No | Path to `apis.yaml` (default: `config/apis.yaml`) | /app/config/apis.yaml |
| DOCCONTEXT_API_URL | If using doccontext | Base URL of DocContext API | http://doccontext.svc:85 |
| DOCCONTEXT_API_TOKEN | If auth=bearer | Bearer token for DocContext (env name in apis.yaml) | (optional) |

\* For semantic search with real DB; otherwise mock data is used.

---

## External APIs (Phase 3)

New external APIs are added **only via config** – no code change.

1. **Config:** Edit `config/apis.yaml` – add an entry under `apis:` with `id`, `base_url_env`, `auth`, `timeout_sec`, and `endpoints` (each with `path`, `method`, `tool_name`, `description`, `params`).
2. **Credentials:** In `.env`, set the env var named in `base_url_env` (e.g. `DOCCONTEXT_API_URL=...`). If the API uses `auth: bearer` or `auth: api_key`, set the var in `auth_env` (e.g. `DOCCONTEXT_API_TOKEN=...`).
3. Restart the MCP server. New tools appear automatically.

APIs whose base URL env is unset are skipped at startup (no error). See `config/apis.yaml` comments for auth options and examples.
