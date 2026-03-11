# PostgreSQL Local Setup – Step by Step

## Step 1: pgAdmin se connect karo

1. **pgAdmin 4** open karo
2. Left sidebar mein **"PostgreSQL 17"** par **double-click** karo
3. Password daalo (install ke time jo diya tha)
4. ✅ Green tick aayega = connected

---

## Step 2: Database banao

1. Left sidebar mein **Databases** par **right-click** karo
2. **Create** → **Database...** select karo
3. **Database** tab mein:
   - **Database:** `istedlal` (ya jo naam chaho)
   - **Owner:** `postgres` (default)
   - Baaki default rehne do
4. **Save** pe click karo

---

## Step 3: pgvector extension enable karo

1. Left sidebar mein **istedlal** database par expand karo
2. **Extensions** par right-click karo
3. **Create** → **Extension...** select karo
4. **Name** dropdown mein **"vector"** select karo (ya type karo)
5. **Save** pe click karo

**Ya SQL se:**

1. **Tools** → **Query Tool** kholo
2. Ye likho:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
3. **Execute** (F5) dabao

---

## Step 4: .env update karo (MCP project)

`.env` file mein:

```
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/istedlal
PGVECTOR_ENABLED=true
```

- `YOUR_PASSWORD` = PostgreSQL install ke time jo password diya tha
- `postgres` = default user
- `5432` = default port
- `istedlal` = jo database naam diya

---

## Step 5: MCP server run karo

```powershell
cd c:\Users\anshu\OneDrive\Desktop\mcp
venv\Scripts\activate
python -m src.main
```

---

## Step 6: Verify karo

- `http://localhost:8000/` – info page
- MCP Inspector ya Cursor se `semantic_search_files` run karo
- **Note:** Abhi tables (chunks, files) nahi hain – schema Phase 2 mein add hoga. PGVECTOR_ENABLED=true hone par bhi agar tables nahi hain to mock fallback use hoga.

---

## Troubleshooting

### Connection refused
- PostgreSQL service Running hai? `Get-Service postgresql-x64-17`

### Authentication failed
- Password sahi hai? pgAdmin mein wahi password use hota hai

### Extension "vector" not found
- pgvector extension PostgreSQL ke saath install hona chahiye. Agar nahi hai to: https://github.com/pgvector/pgvector
