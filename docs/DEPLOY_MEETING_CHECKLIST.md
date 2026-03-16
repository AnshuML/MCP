# Deploy Meeting Checklist – Kal Deploy Ke Liye

**3 log:** Tum (dev), Production/Deploy person, API person.

Yeh doc: (1) API person se **kya puchna hai**, (2) unse milne ke baad **kya fill karna hai**, (3) **Deployment person ko kya dena hai** taaki deploy easy ho aur saare tools sahi output dein.

---

## Part 1: API Person Se Kal Ye Questions Pucho

### 1) DocContext (ya jo bhi external API hai) – Base URL

| # | Tum pucho | API person bata dega | Tum yahan fill karo |
|---|-----------|----------------------|----------------------|
| 1 | "MCP server **production / deploy environment** se tumhare API ko call karega. Wahan se tumhara API ka **exact base URL** kya hoga? (e.g. K8s service URL ya public URL)" | ________________ | **DOCCONTEXT_API_URL** = |

**Example:** `http://doccontext.ogbrain-dev-apps-doccontext.svc.cluster.local:85`  
**Note:** Agar dev vs prod alag URL hon to dono likhwa lo; deploy wale env ke hisaab se ek use karenge.

---

### 2) Auth (token / API key)

| # | Tum pucho | API person bata dega | Tum yahan fill karo |
|---|-----------|----------------------|----------------------|
| 2a | "Is API pe **auth** chahiye? Agar haan – **Bearer token** ya **API key**? Kaun sa **header** use hota hai?" | ________________ | **Auth type:** none / bearer / api_key |
| 2b | "**Token / API key** deploy environment ke liye kaise milega? (static value, ya vault se?)" | ________________ | **DOCCONTEXT_API_TOKEN** (agar chahiye) = |

**Note:** Agar auth nahi chahiye to `config/apis.yaml` mein doccontext block already `auth: none` hai. Agar chahiye to `auth: bearer` ya `auth: api_key` aur `auth_env: DOCCONTEXT_API_TOKEN` set karna padega (main bata dunga deploy se pehle).

---

### 3) Paths / endpoints confirm

| # | Tum pucho | API person bata dega | Tum yahan fill karo |
|---|-----------|----------------------|----------------------|
| 3 | "Ye paths sahi hain? Agar koi **path ya method** alag ho to bata do – hum config mein update kar denge." | ________________ | Path changes (agar koi): |

**Current in apis.yaml:**  
`/register_file_upload`, `/promote_document_scope`, `/list_session_documents`, `/search_documents`, `/get_file_summary`, `/get_file_chunks`, `/get_file_workflow_status`

---

### 4) Network / reachability

| # | Tum pucho | API person bata dega | Tum yahan fill karo |
|---|-----------|----------------------|----------------------|
| 4 | "MCP server **jis cluster/network** pe deploy hoga, wahan se tumhara API **directly reachable** hoga? Agar firewall / VPN chahiye to bata do." | ________________ | Notes for deploy: |

---

## Part 2: Meeting Ke Baad – Ye Values Fill Karo (Deployment Person Ke Liye)

Jab API person ne sab bata diya, **niche wale table mein values bhar do**. Ye same cheez deployment person ko doge – wo inko server ke **.env** (ya K8s ConfigMap/Secret) mein daal dega.

### Deployment Person Ko Dene Wali Values

| Env variable | Value (API person se jo mila) | Required? |
|--------------|------------------------------|-----------|
| **MCP_TRANSPORT** | `streamable-http` | Yes |
| **MCP_BEARER_TOKEN** | (production person / tum decide karo – strong token) | Yes (production) |
| **MCP_RESOURCE_SERVER_URL** | `http://<MCP-server-public-url>:8000/mcp` (deploy URL) | If Bearer auth |
| **MCP_HTTP_STREAMS_ENABLED** | `true` ya `false` (deployment team preference) | No |
| **HTTP_HOST** | `0.0.0.0` | No |
| **HTTP_PORT** | `8000` | No |
| **LOG_LEVEL** | `INFO` | No |
| **DOCCONTEXT_API_URL** | *(API person ne jo base URL diya – Part 1 #1)* | If DocContext tools chahiye |
| **DOCCONTEXT_API_TOKEN** | *(API person ne jo token diya – Part 1 #2b)* | If API needs auth |
| **DATABASE_URL** | *(Agar Phase 2 – DB use karna hai)* | If pgvector |
| **VECTOR_PROVIDER** | `pgvector` ya `mock` | No (default mock) |
| **PGVECTOR_ENABLED** | `true` (if using DB) | No |
| **OLLAMA_URL** | *(Agar semantic search use karna hai)* | If semantic search |
| **OLLAMA_EMBEDDING_MODEL** | `llama3.2` | No |
| **OLLAMA_USERNAME** / **OLLAMA_PASSWORD** | *(If Ollama auth)* | If needed |

---

## Part 3: Deployment Person Ko Kal Ye Bata Dena

1. **Build & run:** `Dockerfile` hai – build karke port **8000** expose karo.  
   Ref: `docs/PRODUCTION_HANDOVER.md`

2. **Env vars:** Part 2 wala table (jo tumne fill kiya) – saare values **.env** ya deployment platform ke env/ConfigMap/Secret mein daalna hai. **.env** kabhi repo mein commit nahi.

3. **Verify:**
   - `curl http://<server>:8000/` → `"status": "running"`
   - MCP Inspector ya n8n se `http://<server>:8000/mcp` connect karke **Tools** list check – built-in + DocContext tools (agar DOCCONTEXT_API_URL set hai) dikhne chahiye.
   - Ek tool (e.g. `get_file_summary` ya `test_echo_get`) run karke output sahi aaye.

4. **Agar DocContext auth chahiye:** `config/apis.yaml` mein doccontext block mein `auth: bearer` (ya `api_key`) aur `auth_env: DOCCONTEXT_API_TOKEN` add karna padega – main (tum) kal meeting ke baad bata dena agar change karna ho.

---

## Short – Kal Tum Kya Karoge

1. **API person se** Part 1 ke questions pucho → unke answers **Part 1 ke tables** mein fill karo.  
2. **Part 2** wala env table bhar do (API + production/deploy values).  
3. **Deployment person ko** ye doc + Part 2 wala filled table de do + bolo: "PRODUCTION_HANDOVER.md bhi dekho; env vars yahi se set karna hai."  
4. Deploy ke baad **verify** wale steps (Part 3) follow karke confirm karo saare tools sahi output de rahe hain.
