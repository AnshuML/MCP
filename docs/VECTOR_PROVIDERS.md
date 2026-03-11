# Vector Search Providers

Semantic search uses a **pluggable provider**. Choose one via `VECTOR_PROVIDER` env var.

---

## Supported Providers

| Provider   | Env Value | Requirements            | Use Case                    |
|------------|-----------|-------------------------|-----------------------------|
| **Mock**   | `mock`    | None                    | Dev, testing (default)      |
| **pgvector** | `pgvector` | PostgreSQL + pgvector extension | Production, existing DB  |
| **ChromaDB** | `chromadb` | `pip install chromadb` | Local, no PostgreSQL       |

---

## Configuration

```env
# Option 1: Mock (default) - no DB, placeholder results
VECTOR_PROVIDER=mock

# Option 2: pgvector - PostgreSQL + pgvector extension
VECTOR_PROVIDER=pgvector
DATABASE_URL=postgresql://user:pass@host:5432/db
PGVECTOR_ENABLED=true

# Option 3: ChromaDB - local, no PostgreSQL
VECTOR_PROVIDER=chromadb
```

---

## pgvector

- **Requires:** PostgreSQL with `vector` extension
- **Schema:** `chunks` (chunk_id, file_id, content_text, page_number, embedding vector(384)), `files` (tenant_id, project_id)
- **Fallback:** If connection/extension fails, falls back to mock

### Version mismatch (e.g. PG 17 vs vector.dll for PG 18)

Use pgvector binaries matching your PostgreSQL version, or switch to `VECTOR_PROVIDER=chromadb` / `mock`.

---

## ChromaDB

- **Install:** `pip install chromadb`
- **Storage:** `data/chroma/` (local directory)
- **Collection:** `file_chunks` with metadata: tenant_id, project_id, file_id, chunk_id, page_number
- **Fallback:** If ChromaDB not installed or query fails, falls back to mock

---

## Adding a New Provider

1. Create `src/providers/vector/your_provider.py`
2. Implement `semantic_search(query, tenant_id, project_id, top_k, file_ids, threshold)` returning `list[dict]` with: chunk_id, file_id, content, page_number, score, provenance
3. Add case in `get_vector_provider()` in `src/providers/vector/__init__.py`
4. Add `VECTOR_PROVIDER=your_provider` support

See `VectorProviderProtocol` in `src/providers/vector/base.py` for the interface.
