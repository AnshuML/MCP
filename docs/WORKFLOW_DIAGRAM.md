# Istedlal MCP Server – Workflow Diagrams

---

## 1. Request Flow (End-to-End)

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ MCP Inspector   │     │ Cursor IDE       │     │ Custom Client   │
│ (HTTP)          │     │ (stdio)          │     │ (HTTP)          │
└────────┬────────┘     └────────┬─────────┘     └────────┬────────┘
         │                       │                        │
         │    http://host:8000/mcp    stdio
         └───────────────────────┬────────────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │   src/main.py          │
                    │   FastMCP Server       │
                    └────────────┬───────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
              ▼                  ▼                  ▼
     ┌────────────────┐ ┌───────────────┐ ┌──────────────────┐
     │ GET /          │ │ Bearer Auth?  │ │ MCP Tool Call    │
     │ (root info)    │ │ (if token set)│ │ (JSON-RPC)       │
     └───────┬────────┘ └───────┬───────┘ └────────┬─────────┘
             │                  │ 401 if invalid   │
             │                  │                  │
             ▼                  ▼                  ▼
     ┌────────────────┐ ┌───────────────┐ ┌──────────────────┐
     │ JSON Response  │ │ Reject        │ │ Route to Tool     │
     │ status, tools  │ │               │ │ get_file_metadata │
     └────────────────┘ └───────────────┘ │ search_files      │
                                          │ semantic_search   │
                                          └────────┬─────────┘
                                                   │
                                                   ▼
                                          ┌──────────────────┐
                                          │ src/tools/       │
                                          │ Tool logic       │
                                          └────────┬─────────┘
                                                   │
                                                   ▼
                                          ┌──────────────────┐
                                          │ Provider/DB      │
                                          │ (mock/pgvector/  │
                                          │  chromadb)       │
                                          └────────┬─────────┘
                                                   │
                                                   ▼
                                          ┌──────────────────┐
                                          │ JSON Response    │
                                          │ → Client         │
                                          └──────────────────┘
```

---

## 2. Mermaid Diagram (Request Flow)

```mermaid
flowchart TB
    subgraph Clients
        A[MCP Inspector]
        B[Cursor IDE]
        C[Custom Client]
    end

    subgraph Server["Istedlal MCP Server"]
        D[main.py - FastMCP]
        E{Bearer Auth?}
        F[Auth OK]
        G[401 Reject]
        H[Tool Router]
        
        subgraph Tools
            T1[get_file_metadata]
            T2[search_files]
            T3[semantic_search_files]
        end
        
        subgraph Providers
            P1[Mock]
            P2[pgvector]
            P3[ChromaDB]
        end
    end

    A -->|HTTP| D
    B -->|stdio| D
    C -->|HTTP| D
    
    D --> E
    E -->|Token valid| F
    E -->|Token invalid| G
    F --> H
    H --> T1
    H --> T2
    H --> T3
    
    T1 --> P1
    T2 --> P1
    T3 --> P1
    T3 --> P2
    T3 --> P3
    
    P1 --> R[Response]
    P2 --> R
    P3 --> R
    R --> A
    R --> B
    R --> C
```

---

## 3. Vector Provider Selection Flow

```mermaid
flowchart LR
    A[semantic_search_files] --> B[get_vector_provider]
    B --> C{VECTOR_PROVIDER?}
    
    C -->|mock| D[MockVectorProvider]
    C -->|pgvector| E[PgVectorProvider]
    C -->|chromadb| F[ChromaDBProvider]
    
    D --> G[Mock results]
    
    E --> H{DB + pgvector OK?}
    H -->|Yes| I[Real search]
    H -->|No| G
    
    F --> J{ChromaDB installed?}
    J -->|Yes| K[ChromaDB search]
    J -->|No| G
    
    I --> L[Results]
    K --> L
    G --> L
```

---

## 4. Component Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Istedlal MCP Server                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────────────┐  │
│  │   config    │    │    auth     │    │         tools               │  │
│  │  .env vars  │    │ Bearer      │    │  get_file_metadata          │  │
│  │             │    │ token verify│    │  search_files               │  │
│  └──────┬──────┘    └──────┬──────┘    │  semantic_search_files      │  │
│         │                  │           └──────────────┬──────────────┘  │
│         │                  │                          │                 │
│         └──────────────────┼──────────────────────────┘                 │
│                            │                                            │
│                            ▼                                            │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                     main.py (FastMCP)                             │   │
│  │  • Transport: stdio | streamable-http                             │   │
│  │  • Routes: /, /favicon.ico, /mcp                                  │   │
│  │  • All hosts allowed (Bearer auth for security)                   │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                            │                                            │
│                            ▼                                            │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │              providers/vector (pluggable)                         │   │
│  │  ┌──────────┐   ┌──────────┐   ┌──────────┐                      │   │
│  │  │  mock    │   │ pgvector │   │ chromadb │                      │   │
│  │  │ (default)│   │ (Postgres)│   │ (local)  │                      │   │
│  │  └──────────┘   └──────────┘   └──────────┘                      │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Deployment Flow

```mermaid
flowchart TB
    subgraph Build
        A[Source Code] --> B[docker build]
        B --> C[istedlal-mcp image]
    end

    subgraph Deploy
        C --> D[docker run / k8s]
        D --> E[Container]
        E --> F[Port 8000]
    end

    subgraph Config
        G[.env / Secrets]
        G --> H[MCP_BEARER_TOKEN]
        G --> I[DATABASE_URL]
        G --> J[VECTOR_PROVIDER]
    end

    H --> E
    I --> E
    J --> E

    subgraph Clients
        K[MCP Inspector]
        L[Cursor]
    end

    F --> K
    F --> L
```

---

**Note:** Mermaid diagrams GitHub, GitLab, VS Code (Markdown Preview), aur Cursor mein render ho sakte hain.
