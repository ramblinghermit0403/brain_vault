# detailed System Design - Brain Vault

## 1. High-Level Architecture (Component View)

```mermaid
graph TB
    subgraph Client_Side [Client Side]
        Browser[WebApp (Vue.js)]
        Extension[Chrome Extension]
    end

    subgraph Load_Balancer [Ingress]
        Nginx[Reverse Proxy / LB]
    end

    subgraph Backend_Core [Backend API (FastAPI)]
        Auth_Mod[Auth & Users]
        Mem_Mod[Memory Management]
        Doc_Mod[Document Processing]
        LLM_Mod[LLM Orchestration]
        WS_Mod[Real-time Notification]
    end

    subgraph Background_Workers [Async Workers]
        Dedupe_Worker[Deduplication Job]
        Vector_Ingest[Vector Ingestion]
    end

    subgraph Data_Persistence [Data Layer]
        Postgres[(Relational DB - Users/Metadata)]
        Chroma[(Vector DB - Embeddings)]
        FileSystem[File Storage (MinIO/Local)]
    end

    Browser -->|HTTPS| Nginx
    Extension -->|HTTPS| Nginx
    Nginx --> Backend_Core
    
    Auth_Mod --> Postgres
    
    Mem_Mod --> Postgres
    Mem_Mod --> Chroma
    Mem_Mod --> WS_Mod
    
    Doc_Mod --> FileSystem
    Doc_Mod --> Vector_Ingest
    
    Vector_Ingest --> Chroma
    Dedupe_Worker --> Postgres
    Dedupe_Worker --> Chroma
    Dedupe_Worker --> WS_Mod
    
    WS_Mod -->|Websocket| Browser
```

## 2. Core Workflows (Sequence Diagrams)

### 2.1 Memory Creation & Ingestion Flow
```mermaid
sequenceDiagram
    participant User
    participant API as API (Memory Router)
    participant DB as SQL Database
    participant Vector as Vector Store
    participant WS as Websocket Manager

    User->>API: POST /memory (Content, Tags)
    API->>DB: Save Memory (Pending)
    DB-->>API: Memory ID
    API->>Vector: Generate Embedding & Upsert
    Vector-->>API: Success
    API->>DB: Update Status (Active)
    API->>WS: Broadcast "MemoryAdded" event
    WS-->>User: Update UI (Real-time)
    API-->>User: 201 Created
```

### 2.2 LLM Interaction with RAG
```mermaid
sequenceDiagram
    participant User
    participant API as API (LLM Router)
    participant Vector as Vector Store
    participant Provider as External LLM (OpenAI/Anthropic)
    
    User->>API: POST /llm/chat (Query)
    API->>Vector: Query(Query Text, Top-K)
    Vector-->>API: Relevant Memories/Docs
    API->>API: Construct Context Window
    API->>Provider: Stream Chat Completion(Prompt + Context)
    loop Stream
        Provider-->>API: Token Chunk
        API-->>User: Token Chunk (SSE/Stream)
    end
```

### 2.3 Background Deduplication
```mermaid
sequenceDiagram
    participant Job as Dedupe Job
    participant DB as SQL Database
    participant Vector as Vector Store
    participant WS as Websocket Manager
    
    loop Every 60s
        Job->>DB: Fetch New Memories
        loop For Each Memory
            Job->>Vector: Search Similar (Threshold < 0.3)
            Vector-->>Job: Candidates
            alt Candidates Found
                Job->>DB: Create Cluster Proposal
                Job->>WS: Send "NewCluster" Notification
            end
        end
    end
```

## 3. Database Schema (ER Diagram)

```mermaid
erDiagram
    Users ||--o{ AIClient : "has keys"
    Users ||--o{ Memories : "owns"
    Users ||--o{ Documents : "owns"
    Users ||--o{ MemoryClusters : "receives"

    Users {
        int id PK
        string email
        string hashed_password
        boolean is_active
    }

    AIClient {
        int id PK
        int user_id FK
        string provider "openai, anthropic"
        string encrypted_api_key
    }

    Memories {
        int id PK
        int user_id FK
        text content
        json tags
        string embedding_id
        string status "pending, active, archived"
    }

    Documents {
        int id PK
        int user_id FK
        string filename
        string file_path
        string mime_type
    }

    MemoryClusters {
        int id PK
        int user_id FK
        json memory_ids
        string representative_text
    }
```

## 4. Application Structure (JSON)

```json
{
  "system": "Brain Vault",
  "layers": [
    {
      "name": "Frontend",
      "tech": ["Vue 3", "Vite", "TailwindCSS"],
      "modules": {
        "Views": ["Dashboard", "Editor", "Login", "Settings"],
        "Components": ["UnifiedList", "MarkdownEditor", "Sidebar"],
        "State": "Pinia"
      }
    },
    {
      "name": "Backend API",
      "tech": ["FastAPI", "Python 3.10", "Pydantic"],
      "routers": [
        { "path": "/auth", "desc": "OAuth2 / JWT Handling" },
        { "path": "/memory", "desc": "CRUD, Tagging" },
        { "path": "/retrieval", "desc": "Vector Semantic Search" },
        { "path": "/user/llm-keys", "desc": "Secure Key Management" },
        { "path": "/ws", "desc": "Websocket Endpoint" }
      ]
    },
    {
      "name": "Services",
      "components": [
        { "name": "VectorStore", "impl": "ChromaDB", "desc": "Embedding management" },
        { "name": "DedupeService", "impl": "Async/Background", "desc": "Similarity clustering" },
        { "name": "EncryptionService", "impl": "Fernet", "desc": "At-rest encryption" }
      ]
    }
  ]
}
```
