# Istedlal MCP Server

MCP Server for Istedlal AI Agents - file metadata, vector search, workflow metrics access.

## Requirements

- Python 3.10+
- See `requirements.txt` for dependencies

## Setup

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Create .env with required variables (see docs/ENV_SETUP.md)
```

## Run

**Terminal testing** (use streamable-http to avoid "Invalid JSON: EOF" errors):
```bash
# .env: MCP_TRANSPORT=streamable-http
python -m src.main
# Server at http://localhost:8000/mcp
```

**Cursor/IDE integration** (stdio - Cursor spawns the process, don't run manually):
```bash
# .env: MCP_TRANSPORT=stdio
# Add server to Cursor MCP settings; Cursor will start it automatically
```

## Tools

- `get_file_metadata` - Fetch metadata for a file by ID
- `search_files` - Search files by metadata filters
- `semantic_search_files` - **Phase 2** - Semantic search over file embeddings (pgvector)

## Testing with MCP Inspector

See **[docs/MCP_INSPECTOR_GUIDE.md](docs/MCP_INSPECTOR_GUIDE.md)** for the complete step-by-step guide.

```bash
npx -y @modelcontextprotocol/inspector
```

---

## Production

### Production Checklist

| Item | Required | Notes |
|------|----------|-------|
| Dockerfile | Yes | Build container image |
| .dockerignore | Yes | Exclude venv, .env, __pycache__ |
| Production .env | Yes | Set on server (never commit) |
| Port 8000 | Yes | Expose for MCP endpoint |
| PostgreSQL | Optional | For real pgvector (Phase 2) |

### What to Exclude from Deployment

- `.cursor/` – Cursor IDE config only, not needed on server
- `venv/` – Create fresh on server or use Docker
- `.env` – Contains secrets; set separately on server
- `__pycache__/` – Python cache, auto-generated
- `data/` – Reference docs only, not runtime

### Production Environment Variables

```
MCP_TRANSPORT=streamable-http
HTTP_HOST=0.0.0.0
HTTP_PORT=8000
DATABASE_URL=postgresql://user:password@db-host:5432/dbname
PGVECTOR_ENABLED=true
LOG_LEVEL=INFO
MCP_BEARER_TOKEN=your-secret-token   # Required – Bearer token auth for /mcp
```

### Dockerfile (Create if Deploying via Docker)

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/
ENV MCP_TRANSPORT=streamable-http
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["python", "-m", "src.main"]
```

### .dockerignore (Create to Exclude from Build)

```
venv/
.env
.git/
.cursor/
__pycache__/
*.pyc
data/
docs/
scripts/
tests/
infra/
```

### Deployment Steps

1. **Build:** `docker build -t istedlal-mcp .`
2. **Run:** `docker run -p 8000:8000 -e DATABASE_URL=... -e MCP_BEARER_TOKEN=your-secret istedlal-mcp`
3. **Verify:** `curl http://localhost:8000/` (info page)
4. **MCP Endpoint:** `http://your-server:8000/mcp`

### Kubernetes (Optional)

- Use Deployment + Service manifests in `infra/k8s/`
- Expose Service (ClusterIP/NodePort/LoadBalancer)
- Set DATABASE_URL via Secret

### Health & Monitoring

- Root `/` returns JSON with status
- MCP endpoint: `/mcp` (for MCP clients only)
- Logs: Set LOG_LEVEL=DEBUG for troubleshooting