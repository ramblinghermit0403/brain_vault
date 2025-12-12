# Brain Vault

A 3-tier personal knowledge management system with AI-powered retrieval and universal LLM integration.

## 🌟 Features

### Tier 1: Universal Prompt Engine
- **Web-based prompt generator** with context retrieval
- **Multiple templates**: Standard Q&A, Code Assistant, Summarization
- **Token-aware compactor** to fit LLM context limits
- **One-click copy** to paste into any LLM (ChatGPT, Claude, Gemini)

### Tier 2: Browser Extension
- **Auto-inject** memory context into web LLMs
- **Page clipper** to save web content to your vault
- **Seamless authentication** via JWT token
- **Supports**: ChatGPT, Claude, Gemini

### Tier 3: MCP Server
- **Model Context Protocol** integration for developer tools
- **Tools exposed**: `search_memory`, `save_memory`, `get_document`
- **Compatible with**: VS Code, Cursor, Claude Desktop, agent frameworks

## 🚀 Quick Start

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

## 📖 Usage Guide

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

## 🏗️ Architecture

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

## 🔧 Configuration

### API Keys

Set your LLM API keys in **Settings**:
- OpenAI API Key (for GPT models)
- Gemini API Key (for Gemini models)

Keys are stored locally in browser `localStorage`.

### Database

SQLite database is created automatically at `backend/brain_vault.db`.

### Vector Store

ChromaDB stores embeddings at `backend/chroma_db/`.

## 🧪 Testing

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

## 📝 API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🛠️ Tech Stack

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

## 🤝 Contributing

This is a personal project, but suggestions are welcome via issues.

## 📄 License

MIT License - feel free to use and modify.

## 🙏 Acknowledgments

- Built with assistance from Antigravity AI
- MCP specification by Anthropic
- Inspired by personal knowledge management best practices
