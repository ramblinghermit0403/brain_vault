import asyncio
import sys
import os
import contextlib
from typing import Any, List, Optional
from mcp.server.fastmcp import FastMCP

# Context manager to redirect stdout to stderr
@contextlib.contextmanager
def redirect_stdout_to_stderr():
    old_stdout = sys.stdout
    sys.stdout = sys.stderr
    try:
        yield
    finally:
        sys.stdout = old_stdout

# Perform imports and initialization with stdout redirected
# This prevents libraries (like ChromaDB) from printing to stdout and breaking the MCP protocol
with redirect_stdout_to_stderr():
    from app.services.vector_store import vector_store
    from app.services.ingestion import ingestion_service
    from app.db.session import SessionLocal
    from app.models.document import Document
    from app.models.user import User
    from app.models.memory import Memory
    from app.services.context_builder import context_builder

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
async def save_memory(text: str, source: str = "mcp", tags: Optional[List[str]] = None) -> str:
    """
    Save a new memory snippet to the Brain Vault.
    Args:
        text: The content of the memory.
        source: Source of memory (default 'mcp').
        tags: Optional list of tags.
    """
    db = SessionLocal()
    try:
        user = get_current_user(db)
        if not user:
            return "Error: No user found."

        # Check Auto-Approve Setting
        auto_approve = True
        user_settings = user.settings
        
        if user_settings:
            # Handle JSON stored as string in SQLite if necessary
            if isinstance(user_settings, str):
                import json
                try:
                    user_settings = json.loads(user_settings)
                except:
                    user_settings = {}
                    
            if isinstance(user_settings, dict):
                auto_approve = user_settings.get("auto_approve", True)
                
        initial_status = "approved" if auto_approve else "pending"
        show_in_inbox = True
        
        import uuid
        embedding_id = str(uuid.uuid4())

        memory = Memory(
            user_id=user.id,
            content=text,
            title=f"Memory from {source}",
            source_llm=source,
            status=initial_status,
            tags=tags,
            embedding_id=embedding_id,
            show_in_inbox=show_in_inbox
        )
        db.add(memory)
        db.commit()
        db.refresh(memory)
        
        # Ingest if approved
        if initial_status == "approved":
            try:
                ids, documents_content, metadatas = ingestion_service.process_text(
                    text=text,
                    document_id=memory.id,
                    title=memory.title,
                    doc_type="memory",
                    metadata={"user_id": user.id, "memory_id": memory.id, "tags": str(tags) if tags else "", "source": source}
                )
                
                if ids:
                    memory.embedding_id = ids[0]
                    db.commit()
                    
                    vector_store.add_documents(ids=ids, documents=documents_content, metadatas=metadatas)
            except Exception as e:
                return f"Memory saved but ingestion failed: {str(e)}"
        
        return f"Memory saved to Inbox with ID: mem_{memory.id} (Status: {initial_status})"
    except Exception as e:
        return f"Error saving memory: {str(e)}"
    finally:
        db.close()

@mcp.tool()
async def search_brain_vault(query: str, purpose: str = "general") -> str:
    """
    The PRIMARY tool for searching your memory. Use this to retrieve relevant context, notes, or code snippets from the Brain Vault.
    Args:
        query: The semantic search query (e.g., "python fastapi project structure" or "notes on meeting with Bob").
        purpose: Optional hint for context formatting ("general", "code", "summary").
    """
    db = SessionLocal()
    try:
        user = get_current_user(db)
        if not user:
            return "Error: No user found."
            
        ctx = context_builder.build_context(query=query, user_id=user.id, limit_tokens=2000)
        return ctx["text"]
    finally:
        db.close()

@mcp.tool()
async def get_inbox() -> str:
    """
    Get list of pending memories in the Inbox.
    """
    db = SessionLocal()
    try:
        user = get_current_user(db)
        if not user:
            return "Error: No user found."
            
        memories = db.query(Memory).filter(
            Memory.user_id == user.id,
            Memory.status == "pending"
        ).order_by(Memory.created_at.desc()).all()
        
        if not memories:
            return "Inbox is empty."
            
        results = []
        for mem in memories:
            results.append(f"ID: mem_{mem.id} | Content: {mem.content[:50]}... | Source: {mem.source_llm}")
            
        return "\n".join(results)
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

@mcp.tool()
async def generate_prompt(query: str, template: str = "standard") -> str:
    """
    Generate a prompt with retrieved context from the vault.
    Args:
        query: The user's question or request.
        template: The template to use ("standard", "code", "summary").
    """
    db = SessionLocal()
    try:
        user = get_current_user(db)
        if not user:
            return "Error: No user found."
            
        # 1. Retrieve Context using ContextBuilder (Standardized)
        ctx = context_builder.build_context(query=query, user_id=user.id, limit_tokens=2000)
        context_str = ctx["text"]
        
        # 3. Apply Template
        if template == "code":
            prompt = f"""You are an expert coding assistant. Use the following context to answer the user's request.

CONTEXT:
{context_str}

USER REQUEST:
{query}

INSTRUCTIONS:
- Provide clear, efficient code.
- Explain your reasoning.
"""
        elif template == "summary":
            prompt = f"""Please summarize the following information based on the user's query.

CONTEXT:
{context_str}

QUERY:
{query}
"""
        else: # Standard
            prompt = f"""Use the following memory context to answer the question.

MEMORY CONTEXT:
{context_str}

QUESTION:
{query}
"""
        return prompt
    finally:
        db.close()

@mcp.tool()
async def update_memory(memory_id: str, content: str) -> str:
    """
    Update the content of an existing memory.
    Args:
        memory_id: The ID of the memory (must start with 'mem_').
        content: The new content.
    """
    if not memory_id.startswith("mem_"):
        return "Error: Only memories (starting with 'mem_') can be updated via this tool."

    db = SessionLocal()
    try:
        user = get_current_user(db)
        if not user:
            return "Error: No user found."

        try:
            mem_id = int(memory_id.split("_")[1])
        except ValueError:
            return "Error: Invalid ID format."

        memory = db.query(Memory).filter(Memory.id == mem_id, Memory.user_id == user.id).first()
        if not memory:
            return "Error: Memory not found."

        # Update DB
        memory.content = content
        db.commit()
        db.refresh(memory)

        # Update Vector Store
        if memory.embedding_id:
            try:
                vector_store.delete(ids=[memory.embedding_id])
            except:
                pass
        
        # Re-ingest
        ids, documents_content, metadatas = ingestion_service.process_text(
            text=memory.content,
            document_id=memory.id,
            title=memory.title,
            doc_type="memory",
            metadata={"user_id": user.id, "memory_id": memory.id, "tags": str(memory.tags) if memory.tags else "", "source": "mcp"}
        )
        
        if ids:
            memory.embedding_id = ids[0]
            db.commit()
            
            vector_store.add_documents(
                ids=ids,
                documents=documents_content,
                metadatas=metadatas
            )

        return f"Memory {memory_id} updated successfully."
    except Exception as e:
        return f"Error updating memory: {str(e)}"
    finally:
        db.close()

@mcp.tool()
async def delete_memory(memory_id: str) -> str:
    """
    Delete a memory or document by ID.
    Args:
        memory_id: The ID of the item (e.g., 'mem_1' or 'doc_5').
    """
    db = SessionLocal()
    try:
        user = get_current_user(db)
        if not user:
            return "Error: No user found."

        if memory_id.startswith("doc_"):
            # Handle Document Deletion
            try:
                doc_id = int(memory_id.split("_")[1])
            except ValueError:
                return "Error: Invalid ID format."

            document = db.query(Document).filter(Document.id == doc_id, Document.user_id == user.id).first()
            if not document:
                return "Error: Document not found."
            
            # Delete chunks from vector store
            for chunk in document.chunks:
                if chunk.embedding_id:
                    try:
                        vector_store.delete(ids=[chunk.embedding_id])
                    except:
                        pass # Ignore vector store errors
            
            db.delete(document)
            db.commit()
            return f"Document {memory_id} deleted successfully."
            
        elif memory_id.startswith("mem_"):
            # Handle Memory Deletion
            try:
                mem_id = int(memory_id.split("_")[1])
            except ValueError:
                return "Error: Invalid ID format."

            memory = db.query(Memory).filter(Memory.id == mem_id, Memory.user_id == user.id).first()
            if not memory:
                return "Error: Memory not found."
            
            if memory.embedding_id:
                try:
                    vector_store.delete(ids=[memory.embedding_id])
                except:
                    pass
                
            db.delete(memory)
            db.commit()
            return f"Memory {memory_id} deleted successfully."
        
        else:
            return "Error: ID must start with 'mem_' or 'doc_'."
    except Exception as e:
        return f"Error deleting item: {str(e)}"
    finally:
        db.close()

@mcp.tool()
async def list_memories(limit: int = 10, offset: int = 0) -> str:
    """
    List recent memories and documents in the vault.
    Args:
        limit: Number of items to return (default 10).
        offset: Pagination offset (default 0).
    """
    db = SessionLocal()
    try:
        user = get_current_user(db)
        if not user:
            return "Error: No user found."
            
        # Fetch Memories
        memories = db.query(Memory).filter(Memory.user_id == user.id).order_by(Memory.created_at.desc()).limit(limit).offset(offset).all()
        
        # Fetch Documents (simple logic, separate query for now)
        documents = db.query(Document).filter(Document.user_id == user.id).order_by(Document.created_at.desc()).limit(limit).offset(offset).all()
        
        results = []
        for mem in memories:
            results.append(f"[Memory] ID: mem_{mem.id} | Title: {mem.title} | Created: {mem.created_at}")
            
        for doc in documents:
            results.append(f"[Document] ID: doc_{doc.id} | Title: {doc.title} | Type: {doc.file_type} | Created: {doc.created_at}")
            
        if not results:
            return "No memories found."
            
        return "\n".join(results)
    finally:
        db.close()

# --- RESOURCES ---
@mcp.resource("brain://inbox")
async def get_inbox_resource() -> str:
    """
    Read the current contents of the Inbox directly as a resource.
    """
    db = SessionLocal()
    try:
        user = get_current_user(db)
        if not user:
            return "Error: No user found."
            
        memories = db.query(Memory).filter(
            Memory.user_id == user.id,
            Memory.status == "pending"
        ).order_by(Memory.created_at.desc()).all()
        
        if not memories:
            return "Inbox is empty."
            
        results = ["# Brain Vault Inbox"]
        for mem in memories:
            results.append(f"- [ID: mem_{mem.id}] ({mem.source_llm}): {mem.content[:100]}...")
            
        return "\n".join(results)
    finally:
        db.close()

# --- PROMPTS ---
@mcp.prompt()
def daily_briefing() -> str:
    """
    Generate a briefing prompt based on recent memories.
    """
    return "Please review my recent memories from the Brain Vault and provide a summary of what I've been working on and any outstanding tasks in my Inbox."

@mcp.prompt()
def project_context(project_name: str) -> str:
    """
    Generate a prompt to focus on a specific project.
    """
    return f"Please search the Brain Vault for all information related to '{project_name}'. Summarize the key points, technical decisions, and current status."

@mcp.tool()
async def search_by_date(start_date: str, end_date: Optional[str] = None) -> str:
    """
    Find memories created within a specific date range.
    Args:
        start_date: Start date in YYYY-MM-DD format.
        end_date: End date in YYYY-MM-DD format (optional, defaults to end of start_date).
    """
    db = SessionLocal()
    try:
        user = get_current_user(db)
        if not user:
            return "Error: No user found."
            
        from datetime import datetime, timedelta
        
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            if end_date:
                end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1) # Inclusive of end date
            else:
                end = start + timedelta(days=1)
        except ValueError:
            return "Error: Invalid date format. Use YYYY-MM-DD."
            
        memories = db.query(Memory).filter(
            Memory.user_id == user.id,
            Memory.created_at >= start,
            Memory.created_at < end
        ).order_by(Memory.created_at.asc()).all()
        
        if not memories:
            return f"No memories found between {start_date} and {end_date or start_date}."
            
        results = []
        for mem in memories:
            results.append(f"[{mem.created_at.strftime('%Y-%m-%d %H:%M')}] {mem.title}: {mem.content[:200]}...")
            
        return "\n".join(results)
    finally:
        db.close()

@mcp.tool()
async def get_all_tags() -> str:
    """
    Get a list of all tags currently used in the Brain Vault. 
    Use this to understand the taxonomy of the user's knowledge.
    """
    db = SessionLocal()
    try:
        user = get_current_user(db)
        if not user:
            return "Error: No user found."
        
        # Inefficient but valid for MVP: Fetch all and aggregate
        memories = db.query(Memory).filter(Memory.user_id == user.id).all()
        
        all_tags = set()
        for mem in memories:
            if mem.tags:
                try:
                    # mem.tags might be a list or a string repr of list depending on SQLite/JSON handling
                    tags_list = mem.tags if isinstance(mem.tags, list) else eval(mem.tags)
                    for tag in tags_list:
                        all_tags.add(tag)
                except:
                    pass
                    
        sorted_tags = sorted(list(all_tags))
        
        if not sorted_tags:
            return "No tags found."
            
        return "Current Tags:\n" + ", ".join([f"#{t}" for t in sorted_tags])
    finally:
        db.close()

if __name__ == "__main__":
    mcp.run()
