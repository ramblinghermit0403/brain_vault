# MemWyre

Your Second Brain, Supercharged.

MemWyre is a universal memory layer for AI—designed to capture, organize, and retrieve your knowledge across tools, conversations, and large language models.

Instead of losing context every time you switch between ChatGPT, Gemini, Claude, editors, or agents, MemWyre becomes the persistent brain that follows you everywhere.

## Demo

[![Watch the demo](https://img.youtube.com/vi/3lsy-Wnhj28/0.jpg)](https://youtu.be/3lsy-Wnhj28)

## The Problem

Today’s AI tools are powerful—but stateless.
Every chat starts from zero
Important insights get lost in conversations
Knowledge is scattered across PDFs, chats, docs, videos, and web pages
Each LLM lives in its own silo
Users are forced to re-explain themselves endlessly
Existing tools solve storage or note-taking, but not memory continuity for AI.
AI forgot. Again.

## What MemWyre Solves

MemWyre introduces a shared, intelligent memory system that sits outside any single LLM and works with all of them.

It enables:
Long-term memory for AI workflows
Cross-LLM knowledge reuse
Contextual retrieval grounded in your own data
A clean separation between thinking (LLMs) and remembering (MemWyre)
MemWyre doesn’t replace AI tools—it augments them.

## Key Features
### Unified Memory Vault

Store everything in one place:

Chat outputs
Documents (PDF, DOC, Markdown)
Web pages & research
Notes, ideas, decisions
Agent outputs

All content is automatically processed, chunked, embedded, and indexed for semantic retrieval.

### Smart Memory (Not Just Storage)

MemWyre goes beyond dumping files:
Semantic chunking
Auto-generated embeddings
Metadata & source tracking
Context-aware retrieval
Inbox-based memory approval flow
Memory becomes queryable intelligence, not dead notes.

### Contextual Retrieval Engine

Ask questions and get answers grounded in your own memory, not hallucinations.

Vector search
Top-K relevance ranking
Source-linked context
Optional summaries

Works as a standalone search or as context injected into LLM prompts.

### LLM-Agnostic by Design

MemWyre is not tied to any single model.
It integrates via:
API-based LLM connectors
MCP servers (for editors & agents)
Browser extensions
Prompt-level injection (for restricted platforms)

Your memory works across ChatGPT, Gemini, Claude, local models, and future agents.

### Intelligent Memory Inbox

Not all memory should be saved blindly.
MemWyre introduces an Inbox model
Review before committing to long-term memory
Auto-approve trusted sources
Manual control where it matters
Prevents memory pollution

This keeps the system useful, not noisy.

### Multi-Source Ingestion

Bring knowledge from everywhere:

File uploads
Browser extension
Web scraping
YouTube transcripts
Agent outputs
Code editor integrations

All paths lead to the same memory engine.


## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Chrome/Edge browser (for extension)

### Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Backend runs at `http://localhost:8000`

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`

### First-Time Setup

1. Navigate to `http://localhost:5173`
2. **Register** a new account
3. **Login** with your credentials
4. Upload documents or create memories via the dashboard

## Usage Guide

### Tier 1: Prompt Generator

1. Click **"Generate Prompt"** on the dashboard
2. Enter your query (e.g., "Summarize my project notes")
3. Select a template and adjust context size
4. Click **"Generate Prompt"**
5. **Copy** and paste into any LLM

### Tier 2: Browser Extension

#### Installation
1. Open Chrome and go to `chrome://extensions/`
2. Enable **Developer mode**
3. Click **Load unpacked**
4. Select `extension` folder from the project root

#### Usage
1. Click the extension icon
2. Go to **Settings** in Brain Vault web app
3. Click **"Copy Extension Token"**
4. Paste token into extension popup
5. Use the popup to generate prompts or let it auto-inject on supported sites

### Tier 3: MCP Server

#### For Claude Desktop

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "brain-vault": {
      "command": "python",
      "args": ["C:/Users/himan/OneDrive/Documents/brain_vault/backend/mcp_server.py"]
    }
  }
}
```

#### For VS Code / Cursor

Configure your MCP client to run:
```bash
python backend/mcp_server.py
```

#### Available Tools
- `search_memory(query, top_k)` - Search your knowledge base
- `save_memory(text, tags)` - Save new memories
- `get_document(doc_id)` - Retrieve full document content

## Architecture

```
brain_vault/
├── backend/           # FastAPI server
│   ├── app/
│   │   ├── routers/   # API endpoints
│   │   ├── models/    # Database models
│   │   ├── services/  # Business logic
│   │   └── core/      # Config & security
│   ├── mcp_server.py  # MCP server
│   └── requirements.txt
├── frontend/          # Vue.js app
│   ├── src/
│   │   ├── views/     # Pages
│   │   ├── components/# UI components
│   │   └── services/  # API client
│   └── package.json
└── extension/         # Chrome extension
    ├── manifest.json
    ├── background.js
    ├── content.js
    └── popup.html
```

## Configuration

### API Keys

Set your LLM API keys in **Settings**:
- OpenAI API Key (for GPT models)
- Gemini API Key (for Gemini models)

Keys are stored locally in browser `localStorage`.

### Database

SQLite database is created automatically at `backend/brain_vault.db`.

### Vector Store

ChromaDB stores embeddings at `backend/chroma_db/`.

## Testing

### Test MCP Server
```bash
cd backend
venv\Scripts\activate
python test_mcp_live.py
```

### Test Prompt Generation
1. Navigate to `/prompts` in the web app
2. Enter a test query
3. Verify prompt is generated with context

## API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Tech Stack

**Backend:**
- FastAPI
- SQLAlchemy
- ChromaDB
- LangChain
- MCP (Model Context Protocol)

**Frontend:**
- Vue 3
- Vite
- Tailwind CSS
- Monaco Editor

**Extension:**
- Manifest V3
- Chrome Extension APIs

## Contributing

This is a personal project, but suggestions are welcome via issues.

## License

MIT License - feel free to use and modify.

## Acknowledgments

- Built with assistance from Antigravity AI
- MCP specification by Anthropic
- Inspired by personal knowledge management best practices
