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

\* For semantic search with real DB; otherwise mock data is used.
