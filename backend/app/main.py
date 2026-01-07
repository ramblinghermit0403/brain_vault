from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import auth, retrieval, llm, documents, memory, export, prompts, llm_api, inbox, user_keys, ws, settings as user_settings, feedback, chat_api, ingest
from app.db.base import Base
from app.db.session import engine
import app.models # Register models


# Create tables (Async)
# Base.metadata.create_all(bind=engine) -> Moved to startup event

app = FastAPI(
    title="MemWyre",
    description="Backend API for MemWyre - Personal Knowledge Base",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])

app.include_router(retrieval.router, prefix=f"{settings.API_V1_STR}/retrieval", tags=["retrieval"])
app.include_router(llm.router, prefix=f"{settings.API_V1_STR}/llm", tags=["llm"])
app.include_router(documents.router, prefix=f"{settings.API_V1_STR}/documents", tags=["documents"])
app.include_router(ingest.router, prefix=f"{settings.API_V1_STR}/ingest", tags=["ingest"])
app.include_router(memory.router, prefix=f"{settings.API_V1_STR}/memory", tags=["memory"])
app.include_router(export.router, prefix=f"{settings.API_V1_STR}/export", tags=["export"])
app.include_router(prompts.router, prefix=f"{settings.API_V1_STR}/prompts", tags=["prompts"])

# Mount MCP Server (SSE)
# This allows remote connections (e.g. Cursor) via /api/v1/mcp/sse
try:
    # Add backend to path if needed, though usually CWD is backend
    import sys
    import os
    if os.getcwd() not in sys.path:
        sys.path.append(os.getcwd())
    
    # Import mcp object from mcp_server.py
    # Note: This might trigger stdout redirection in mcp_server.py, which is acceptable (logs to stderr)
    from mcp_server import mcp
    
    # Mount the FastMCP SSE app
    app.mount(f"{settings.API_V1_STR}/mcp", mcp.sse_app)
    print("Mounted MCP SSE Server at /api/v1/mcp")
except Exception as e:
    print(f"Failed to mount MCP Server: {e}")
app.include_router(llm_api.router, prefix=f"{settings.API_V1_STR}/llm", tags=["llm-api"])
app.include_router(inbox.router, prefix=f"{settings.API_V1_STR}/inbox", tags=["inbox"])
app.include_router(user_keys.router, prefix=f"{settings.API_V1_STR}/user", tags=["user-keys"])
app.include_router(user_settings.router, prefix=f"{settings.API_V1_STR}/user", tags=["user-settings"])
app.include_router(feedback.router, prefix=f"{settings.API_V1_STR}/feedback", tags=["feedback"])
app.include_router(chat_api.router, prefix=f"{settings.API_V1_STR}/chat", tags=["chat"])
from app.routers import user_api_keys
app.include_router(user_api_keys.router, prefix=f"{settings.API_V1_STR}/user", tags=["api-keys"])
app.include_router(ws.router, prefix="/ws", tags=["websocket"])


@app.on_event("startup")
async def startup_event():
    # Start background tasks
    from app.services.dedupe_job import dedupe_service
    from app.db.session import AsyncSessionLocal
    import asyncio
    
    from app.services.websocket import manager
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # We run it as a background task
    asyncio.create_task(dedupe_service.run_periodic_check(AsyncSessionLocal))
    asyncio.create_task(manager.start_redis_listener())

@app.get("/")
async def root():
    return {"message": "Welcome to MemWyre API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
