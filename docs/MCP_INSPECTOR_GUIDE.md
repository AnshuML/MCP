# MCP Inspector – Complete Guide

Istedlal MCP Server ko test karne ke liye MCP Inspector ka use kaise karein.

---

## Prerequisites

1. **Node.js** installed (npx ke liye)
2. **MCP Server** already running on `http://localhost:8000/mcp`

---

## Step 1: MCP Server Start Karein

Pehle apna MCP server chalayein:

```powershell
cd c:\Users\anshu\OneDrive\Desktop\mcp
venv\Scripts\activate
python -m src.main
```

Server start hone par aisa output dikhega:
```
[INFO] Uvicorn running on http://0.0.0.0:8000
```

**Note:** `.env` mein `MCP_TRANSPORT=streamable-http` hona chahiye.

---

## Step 2: MCP Inspector Launch Karein

**Naya terminal** open karein (server wala band mat karein) aur run karein:

```powershell
npx -y @modelcontextprotocol/inspector
```

Yeh command:
1. Inspector package download karegi (pehli baar)
2. Inspector UI open karegi – usually browser mein `http://localhost:6274` pe

---

## Step 3: Server Se Connect Karein

### Option A: Streamable HTTP (Already Running Server)

1. Inspector UI open hone ke baad **"Add new server"** ya **"Connect"** par click karein
2. **Transport type** mein **"Streamable HTTP"** / **"HTTP"** select karein
3. **URL** field mein yeh daalein:
   ```
   http://localhost:8000/mcp
   ```
   ya
   ```
   http://127.0.0.1:8000/mcp
   ```
4. **Bearer token (agar `.env` mein `MCP_BEARER_TOKEN` set hai):**  
   Inspector mein **Headers** / **Auth** section mein add karein:  
   - Header name: `Authorization`  
   - Value: `Bearer <apna-token>` (token wahi jo `.env` ke `MCP_BEARER_TOKEN` mein hai)
5. **Connect** par click karein

### Option B: Direct Python Server (Inspector Server Start Karega)

Agar Inspector se hi server start karna ho:

```powershell
npx -y @modelcontextprotocol/inspector uv --directory c:\Users\anshu\OneDrive\Desktop\mcp run --with mcp python -m src.main
```

*(Note: `uv` install hona chahiye. Nahi hai to Option A use karein.)*

---

## Step 4: Tools Tab Mein Tools Dekhein

Connect hone ke baad:

1. **Tools** tab pe jayein
2. Wahan ye tools dikhenge:
   - **get_file_metadata**, **search_files**, **semantic_search_files** (built-in)
   - Agar `DOCCONTEXT_API_URL` set hai to Phase 3 external tools bhi (e.g. register_file_upload, search_documents, …)

---

## Step 5: Tool Run Karein

### get_file_metadata

1. **get_file_metadata** par click karein
2. Input fields mein daalein:
   - **file_id:** `test-file-001`
   - **tenant_id:** `tenant-1`
   - **project_id:** `project-1`
3. **Run** / **Execute** par click karein
4. Result panel mein response dikhega (abhi mock data)

### search_files

1. **search_files** par click karein
2. Input fields:
   - **tenant_id:** `tenant-1`
   - **project_id:** `project-1`
   - **filters:** `{}` (empty object) ya `{"processing_status": "completed"}`
   - **page:** `1`
   - **page_size:** `20`
3. **Run** par click karein

---

## Troubleshooting

### Inspector open nahi ho raha

```powershell
npx -y @modelcontextprotocol/inspector@latest
```

### "Connection refused" / "Failed to connect"

- Check karein MCP server chal raha hai: `http://localhost:8000/mcp` browser mein open karein  
- Agar 406 Not Acceptable aaye to normal hai – Inspector se connect karein

### Port 6274 pe kuch nahi khul raha

- Inspector ka URL check karein: terminal mein jo URL print hua hoga wahi use karein
- Firewall / antivirus check karein

### Tools nahi dikh rahe

- Server restart karein
- Inspector se disconnect karke dubara connect karein

---

## Quick Reference

| Step              | Command / Action                              |
|-------------------|-----------------------------------------------|
| 1. Start server   | `python -m src.main`                          |
| 2. Start Inspector| `npx -y @modelcontextprotocol/inspector`      |
| 3. Connect URL    | `http://localhost:8000/mcp`                   |
| 4. Auth (if used) | Header: `Authorization: Bearer <token>`       |
| 5. Test tool      | Tools tab → get_file_metadata / search_files / semantic_search_files |

**n8n se check karne ke liye:** [MCP_INSPECTOR_AND_N8N_CHECKLIST.md](MCP_INSPECTOR_AND_N8N_CHECKLIST.md) – dono Inspector aur n8n ka short checklist.

---

## Inspector Features

- **Tools tab** – tools list, schemas, run karna
- **Resources tab** – resources (agar add kiye hon)
- **Prompts tab** – prompts (agar add kiye hon)
- **Notifications** – server logs / events
