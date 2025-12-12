# **AI Brain Vault — Software Requirements Specification (SRS)**

## **1. Introduction**
### **1.1 Purpose**
The purpose of this document is to define the complete Software Requirements Specification (SRS) for **AI Brain Vault**, a centralized, AI-ready personal and professional knowledge storage platform that can be used to provide contextual memory to any LLM (ChatGPT, Claude, Gemini, etc.).

The system will allow users to:
- Upload and store documents (PDF, DOCX, TXT, MD, images)
- Extract, chunk, and embed text for semantic search and retrieval
- Maintain editable personal/professional memory profiles
- Retrieve relevant context for LLM queries
- Integrate with LLMs through connectors
- Save web content via a browser extension
- Export their entire knowledge base in human-readable and machine-readable formats

### **1.2 Scope**
This MVP targets individual users and professional users who require a unified, portable, and AI-ready knowledge base. The system delivers:
- A secure web app
- A backend retrieval API
- A vector-DB-based semantic memory engine
- A Chrome extension for quick capture
- Basic integrations with ChatGPT and Claude

### **1.3 Definitions, Acronyms, and Abbreviations**
- **LLM** — Large Language Model
- **RAG** — Retrieval-Augmented Generation
- **Embedding** — Vector representation of text
- **Chunking** — Breaking text into manageable pieces
- **Vector DB** — Database optimized for vector search

### **1.4 Overview**
This SRS includes functional requirements, non-functional requirements, system architecture, APIs, workflows, database design, UI sketches, and development milestones.

---

## **2. Overall Description**
### **2.1 Product Perspective**
AI Brain Vault is a standalone product with integrations to external LLM APIs. It consists of:
- Web frontend (Vue.js)
- Backend (FastAPI)
- Vector DB (Chroma or Qdrant)
- Browser extension
- Cloud or local deployment

### **2.2 Product Features Summary**
- User authentication
- Document ingestion + OCR
- AI-powered chunking and embedding
- Metadata tagging
- Memory editor
- Semantic retrieval API
- LLM connectors
- Chrome extension for quick capture
- Export capabilities (Markdown & JSON)

### **2.3 User Classes and Characteristics**
1. **Individual users:** Students, researchers, creators
2. **Tech power users:** Developers, AI enthusiasts
3. **Professional users:** Consultants, managers
4. **Future enterprise teams:** Knowledge workers, analysts

### **2.4 Operating Environment**
- Modern browsers
- Hosted backend (e.g., Railway/Render/Vercel backend)
- Chrome extension
- Optional local deployment

### **2.5 Design and Implementation Constraints**
- Must comply with data privacy norms
- Must support API keys for model providers
- Vector DB must support user-level data isolation

### **2.6 User Documentation**
- Onboarding tutorial
- API usage guide
- Extension usage guide

---

## **3. System Features**
### **3.1 User Authentication**
**Description:** Register/login using email + password. JWT for sessions.

**Functional Requirements:**
- FR1: User can register
- FR2: User can log in
- FR3: User can reset password
- FR4: System verifies JWT on each request

---

### **3.2 File Upload & Ingestion**
**Description:** Upload files → extract text → process → embed → store.

**Functional Requirements:**
- FR1: User can upload PDFs, DOCX, TXT, MD
- FR2: Extract text from each file
- FR3: Chunk text into ~300-token segments
- FR4: Generate embeddings for each chunk
- FR5: Store embeddings + metadata in vector DB
- FR6: Show upload history

---

### **3.3 Memory Editor**
**Description:** User can write/edit personal profiles used for context.

**Functional Requirements:**
- FR1: User can create/edit memory notes
- FR2: System embeds memory notes
- FR3: Notes can have tags and categories
- FR4: Notes show revision history

---

### **3.4 Retrieval Engine**
**Description:** Given a query, system returns the most relevant chunks.

**Functional Requirements:**
- FR1: Accepts query + user ID
- FR2: Performs vector similarity search
- FR3: Returns top_k chunks with metadata
- FR4: Prepares summarized context when requested

---

### **3.5 LLM Connectors**
**Description:** Allow context-aware querying through ChatGPT and Claude.

**Functional Requirements:**
- FR1: User can save API keys
- FR2: System can send context + query to LLM
- FR3: System displays LLM response

---

### **3.6 Browser Extension**
**Description:** Save web content instantly to vault.

**Functional Requirements:**
- FR1: Capture selected text or full page
- FR2: Send sanitized text to backend
- FR3: Tag the content
- FR4: Store in vector DB

---

### **3.7 Export System**
**Description:** Export entire knowledge base.

**Functional Requirements:**
- FR1: Export in Markdown
- FR2: Export in JSON
- FR3: Include metadata

---

## **4. External Interface Requirements**
### **4.1 User Interface (UI)**
- Clean, minimalist dashboard
- File upload page
- Memory editor (Notion-like minimal editor)
- Retrieval test interface
- Settings page for API keys
- Export page

### **4.2 API Interface**
#### Auth
```
POST /auth/register
POST /auth/login
POST /auth/reset
```

#### Upload
```
POST /upload
GET /documents
DELETE /documents/{id}
```

#### Memory
```
POST /memory
GET /memory
PUT /memory/{id}
DELETE /memory/{id}
```

#### Retrieval
```
POST /retrieve
```

#### LLM Connect
```
POST /llm/chatgpt
POST /llm/claude
```

#### Export
```
GET /export/md
GET /export/json
```

---

## **5. System Architecture**
### **5.1 Backend Architecture (FastAPI)**
- Routes
- Auth service
- File processing service
- Text extraction module
- Chunking pipeline
- Embedding generator (OpenAI/Local)
- Vector DB service
- LLM connector service

### **5.2 Frontend Architecture (Vue.js)**
- Auth pages
- Dashboard
- File manager
- Memory editor
- Query tester
- Settings
- Export

### **5.3 Browser Extension Architecture**
- Popup UI
- Content script
- Background service
- API client

### **5.4 Vector Database Schema**
Collections:
- `user_documents`
- `user_memory`
- `web_clips`

Fields:
- id
- user_id
- chunk_text
- embedding
- tags
- source
- created_at

---

## **6. Non-Functional Requirements**
### **6.1 Security**
- JWT auth
- HTTPS only
- Isolation per user

### **6.2 Performance**
- Embedding generation < 3 seconds per 1,000 words
- Retrieval < 200 ms

### **6.3 Scalability**
- Support thousands of embeddings per user
- Horizontal scaling via stateless backend

### **6.4 Reliability**
- Auto-retry on API failure
- Error logging

### **6.5 Usability**
- Minimal learning curve
- Mobile-friendly web app

---

## **7. Database Design**
### **7.1 Tables**
**Users**
- id
- email
- password_hash
- created_at

**Documents**
- id
- user_id
- title
- source
- tags
- created_at

**Chunks**
- id
- document_id
- user_id
- chunk_text
- embedding
- tags

**Memory Profiles**
- id
- user_id
- title
- content
- embedding

---

## **8. System Workflows**
### **8.1 Upload Workflow**
User → Upload File → Extract → Chunk → Embed → Store → Confirm

### **8.2 Retrieval Workflow**
User query → Embedding → Similarity search → Top K chunks → Return context

### **8.3 LLM Query Workflow**
Retrieve context → Send to GPT/Claude → LLM response → Display

### **8.4 Browser Extension Workflow**
User selects text → Click “Send to Vault” → Backend stores → Shows in UI

---

## **9. Development Timeline (3–4 weeks)**
### Week 1:
- Auth
- Upload module
- Extraction
- Chunking
- Embedding pipeline

### Week 2:
- Memory editor
- Retrieval API
- Vector DB integration
- LLM connectors

### Week 3:
- Browser extension
- Export functionality
- UI polish

### Week 4:
- Deployment
- Testing
- Beta launch

---

## **10. Future Enhancements**
- Multi-user shared spaces
- Role-based access
- Automatic summarization
- Multi-model memory sync
- AI agent integration

---

# **END OF DOCUMENT**