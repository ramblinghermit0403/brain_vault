import asyncio
import sys
import os
from typing import Any, List, Optional
from mcp.server.fastmcp import FastMCP

from app.services.vector_store import vector_store
from app.services.ingestion import ingestion_service
from app.db.session import SessionLocal
from app.models.document import Document
from app.models.user import User

# Initialize FastMCP Server
mcp = FastMCP("Brain Vault")

# Helper to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(db):
    """
    Get the current user based on environment variables or fallback to first user.
    """
    # 1. Try env var for email
    user_email = os.environ.get("BRAIN_VAULT_USER_EMAIL")
    if user_email:
        user = db.query(User).filter(User.email == user_email).first()
        if user:
            return user
            
    # 2. Try env var for ID
    user_id = os.environ.get("BRAIN_VAULT_USER_ID")
    if user_id:
        user = db.query(User).filter(User.id == int(user_id)).first()
        if user:
            return user
            
    # 3. Fallback to first user (MVP/Single User mode)
    return db.query(User).first()

@mcp.tool()
async def search_memory(query: str, top_k: int = 5) -> str:
    """
    Search the Brain Vault memory for relevant context.
    Args:
        query: The search query.
        top_k: Number of results to return.
    """
    db = SessionLocal()
    try:
        user = get_current_user(db)
        if not user:
            return "Error: No user found."
            
        # Filter by user_id
        results = vector_store.query(query, n_results=top_k, where={"user_id": user.id})
        
        if not results["documents"] or not results["documents"][0]:
            return "No relevant memories found."
        
        # Format results
        formatted_results = []
        for i, doc in enumerate(results["documents"][0]):
            formatted_results.append(f"Result {i+1}:\n{doc}")
        
        return "\n\n---\n\n".join(formatted_results)
    finally:
        db.close()

@mcp.tool()
async def save_memory(text: str, tags: Optional[List[str]] = None) -> str:
    """
    Save a new memory snippet to the Brain Vault.
    Args:
        text: The content of the memory.
        tags: Optional list of tags.
    """
    # For MVP, we'll assume a default user or require user_id in a real scenario
    # Here we just use the ingestion service to process the text
    # Note: In a real multi-user app, we'd need to handle auth context here
    
    # We need to create a Document record first to get an ID
    db = SessionLocal()
    try:
        user = get_current_user(db)
        if not user:
            return "Error: No user found in database to attach memory to."

        doc = Document(
            title="MCP Memory",
            content=text,
            doc_type="memory",
            user_id=user.id
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        
        # Ingest
        embedding_ids, chunk_texts, metadatas = ingestion_service.process_text(
            text=text,
            document_id=doc.id,
            title="MCP Memory",
            doc_type="memory",
            metadata={"source": "mcp", "tags": ",".join(tags or []), "user_id": user.id}
        )
        
        # FIX: Actually save to vector store
        vector_store.add_documents(
            ids=embedding_ids,
            documents=chunk_texts,
            metadatas=metadatas
        )
        
        return f"Memory saved successfully with ID: {doc.id}"
    except Exception as e:
        return f"Error saving memory: {str(e)}"
    finally:
        db.close()

@mcp.tool()
async def get_document(doc_id: int) -> str:
    """
    Retrieve the full content of a specific document by ID.
    Args:
        doc_id: The ID of the document.
    """
    db = SessionLocal()
    try:
        user = get_current_user(db)
        if not user:
            return "Error: No user found."
            
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            return f"Document with ID {doc_id} not found."
            
        # Check ownership
        if doc.user_id != user.id:
             return f"Document with ID {doc_id} not found (Access Denied)."
             
        return doc.content
    finally:
        db.close()

if __name__ == "__main__":
    mcp.run()
