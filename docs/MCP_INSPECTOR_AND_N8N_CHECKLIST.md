# MCP Inspector & n8n – Check Checklist

Istedlal MCP Server ko **MCP Inspector** aur **n8n** se verify karne ke liye step-by-step.

---

## Pehle yeh ensure karein

1. **Server chal raha ho**
   ```powershell
   cd c:\Users\anshu\OneDrive\Desktop\mcp
   venv\Scripts\activate
   python -m src.main
   ```
   Output: `Uvicorn running on http://0.0.0.0:8000`

2. **Health check**
   - Browser ya curl: `http://localhost:8000/`  
   - Response: `{"status":"running","mcp_endpoint":"/mcp",...}`

3. **Auth (agar `.env` mein `MCP_BEARER_TOKEN` set hai)**  
   Har request ke saath header bhejna hoga:  
   `Authorization: Bearer <token>`  
   (Token wo hi hona chahiye jo `.env` mein `MCP_BEARER_TOKEN` mein hai.)

---

## Part 1: MCP Inspector se check

### Step 1: Inspector chalao

Naya terminal (server wala band mat karo):

```powershell
npx -y @modelcontextprotocol/inspector
```

Browser mein open ho jata hai (usually `http://localhost:6274`).

### Step 2: Server se connect

1. **"Add new server"** / **"Connect"** par click karo.
2. **Transport:** **Streamable HTTP** / **HTTP** choose karo.
3. **URL:** `http://localhost:8000/mcp` (ya `http://127.0.0.1:8000/mcp`).
4. **Bearer token (agar server pe set hai):**
   - Inspector mein **Headers** / **Auth** section dekho.
   - Add header: `Authorization` = `Bearer <apna-token>`  
   (Token wahi jo `.env` mein `MCP_BEARER_TOKEN` hai.)
5. **Connect** par click karo.

### Step 3: Tools verify karo

- **Tools** tab mein ye dikhne chahiye:
  - `get_file_metadata`
  - `search_files`
  - `semantic_search_files`
  - Agar `DOCCONTEXT_API_URL` set hai to Phase 3 tools bhi (e.g. `register_file_upload`, `search_documents`, …).

### Step 4: Ek tool run karo

- **get_file_metadata** choose karo → file_id: `test-file-001`, tenant_id: `tenant-1`, project_id: `project-1` → **Run**.
- Response JSON mein file metadata ya `processing_status: "not_found"` aana chahiye.

**Agar 401 / invalid_token aaye:**  
Inspector mein `Authorization: Bearer <sahi-token>` add karke dubara connect karo.

---

## Part 2: n8n se check

### n8n kahan chal raha hai (URL choose karo)

| n8n kahan hai        | MCP server URL (n8n se use karein)        |
|----------------------|--------------------------------------------|
| Same machine (local) | `http://localhost:8000/mcp`                |
| n8n Docker mein      | `http://host.docker.internal:8000/mcp`     |
| n8n K8s, same ns      | `http://<mcp-service-name>:8000/mcp`       |
| n8n K8s, alag ns      | `http://<mcp-service>.<namespace>.svc.cluster.local:8000/mcp` |

### n8n mein MCP / HTTP setup

1. **Credentials**
   - Agar server pe Bearer token hai to n8n mein ek **Header Auth** credential banao:
     - Name: `Authorization`
     - Value: `Bearer <your-MCP_BEARER_TOKEN>`

2. **MCP tool call (generic HTTP se)**
   - n8n mein **HTTP Request** node use karke MCP endpoint hit karna protocol-specific hai (JSON-RPC style).  
   - Agar n8n ke paas **MCP** / **Model Context Protocol** node hai to:
     - **Server URL:** upar wale table se (e.g. `http://localhost:8000/mcp`).
     - **Authentication:** Header Auth use karo, `Authorization: Bearer <token>`.
   - Tool list / tool call exact format ke liye n8n MCP node ka docs dekho.

3. **Quick connectivity check (n8n se)**
   - Ek **HTTP Request** node:
     - Method: **GET**
     - URL: `http://localhost:8000/` (ya Docker/K8s ke hisaab se `http://host.docker.internal:8000/` etc.)
     - Auth: same Bearer header (agar root pe auth nahi hai to bina auth bhi chal jayega).
   - Run karo → response mein `"status":"running"` aana chahiye.  
   Isse confirm ho jata hai n8n se MCP server reachable hai; uske baad MCP node se tools test karo.

### Agar n8n "Could not connect" de

- n8n **Docker** mein hai to URL **`http://host.docker.internal:8000/mcp`** use karo (localhost mat use karo).
- **K8s** mein dono same namespace mein hon to sirf service name: `http://<mcp-service>:8000/mcp`.
- Firewall / network policy check karo; MCP server `0.0.0.0:8000` pe bind hona chahiye.

---

## Quick reference

| Check              | Action |
|--------------------|--------|
| Server running     | `python -m src.main` → `http://0.0.0.0:8000` |
| Health             | `curl http://localhost:8000/` → `status: running` |
| MCP Inspector      | `npx -y @modelcontextprotocol/inspector` → URL `http://localhost:8000/mcp` + Bearer (if set) |
| n8n (local)        | MCP URL `http://localhost:8000/mcp` |
| n8n (Docker)       | MCP URL `http://host.docker.internal:8000/mcp` |
| 401 / invalid_token| Client request mein `Authorization: Bearer <token>` add karo |

Zyada detail: **MCP Inspector** → [docs/MCP_INSPECTOR_GUIDE.md](MCP_INSPECTOR_GUIDE.md), **Production/URLs** → [docs/PRODUCTION_HANDOVER.md](PRODUCTION_HANDOVER.md).
