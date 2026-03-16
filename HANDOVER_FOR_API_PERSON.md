# MCP Server – API Person Ko Setup & Test Guide

Ye zip MCP server ka code hai. Aap credentials add karke API tools (e.g. DocContext) test kar sakte ho.

---

## 1. Setup (ek baar)

1. **Python 3.10+** installed hona chahiye.
2. **.env file banao:**
   - Root folder mein `.env.example` file hai — usko **copy** karke naam **`.env`** kar do.
   - `.env` open karo aur apne **actual values** daalo (see below).
3. **Dependencies install karo:**
   ```bash
   pip install -r requirements.txt
   ```

---

## 2. .env mein kya fill karna hai

**Minimum (sirf MCP chalane ke liye):**
```env
MCP_TRANSPORT=streamable-http
HTTP_PORT=8000
```

**DocContext API tools dikhane ke liye (Phase 3):**
```env
DOCCONTEXT_API_URL=http://<your-doccontext-base-url>:85
```
Agar DocContext API ko auth chahiye (Bearer/API key) to:
```env
DOCCONTEXT_API_TOKEN=<your-token>
```
*(Aur `config/apis.yaml` mein doccontext block mein `auth: bearer` ya `auth: api_key` aur `auth_env: DOCCONTEXT_API_TOKEN` set karna padega.)*

**Optional – MCP pe auth (production):**
```env
MCP_BEARER_TOKEN=your-secret-token
```

---

## 3. Server run karo

```bash
python -m src.main
```

Output: `Uvicorn running on http://0.0.0.0:8000`

---

## 4. Check karo

1. **Browser:** `http://localhost:8000/` — `"status": "running"` dikhna chahiye.
2. **MCP Inspector:**  
   - Run: `npx -y @modelcontextprotocol/inspector`  
   - Connect URL: `http://localhost:8000/mcp`  
   - Agar `MCP_BEARER_TOKEN` set hai to Header: `Authorization: Bearer <token>`  
   - **Tools** tab mein built-in tools + DocContext tools (agar `DOCCONTEXT_API_URL` set hai) dikhne chahiye.
3. **n8n:** MCP Client node → MCP Endpoint URL: `http://localhost:8000/mcp` → same tools list.

---

## 5. Agar naya API add karna ho

- **config/apis.yaml** — naya block add karo (id, base_url_env, auth, endpoints). Details file ke andar comments mein hain.
- **.env** — naye env vars add karo (base URL, token).
- **Code change nahi.** Server restart karo.

---

**Questions:** Jo person ne zip bheja hai unse contact karein.
