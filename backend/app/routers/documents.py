from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import shutil
import os
import uuid
from datetime import datetime

from app.api import deps
from app.models.user import User
from app.models.document import Document, Chunk
from app.services.vector_store import vector_store
from app.services.ingestion import ingestion_service
from app.services.metadata_extraction import metadata_service
from app.db.session import AsyncSessionLocal

# Wrapper to run in background with fresh session
async def run_metadata_extraction(memory_id: int, user_id: int):
    async with AsyncSessionLocal() as db:
        try:
            await metadata_service.process_memory_metadata(memory_id, user_id, db)
        except Exception as e:
            print(f"Error in background metadata extraction: {e}")

# Text Extraction Libraries
import pdfplumber
import docx
from bs4 import BeautifulSoup

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def extract_text_from_file(file_path: str, file_type: str) -> str:
    text = ""
    try:
        if file_type == "pdf":
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
        elif file_type == "docx":
            doc = docx.Document(file_path)
            for para in doc.paragraphs:
                text += para.text + "\n"
        elif file_type in ["txt", "md"]:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
        elif file_type == "html":
             with open(file_path, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f, "html.parser")
                text = soup.get_text()
    except Exception as e:
        print(f"Error extracting text: {e}")
    return text

@router.post("/upload", response_model=Any)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Upload a document, extract text, chunk it, and store in Vector DB.
    """
    file_ext = file.filename.split(".")[-1].lower()
    if file_ext not in ["pdf", "docx", "txt", "md", "html"]:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    
    # Save file temporarily
    file_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}.{file_ext}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Extract Text
    text = extract_text_from_file(file_path, file_ext)
    if not text.strip():
        os.remove(file_path)
        raise HTTPException(status_code=400, detail="Could not extract text from file")
        
    # Create Document Record
    document = Document(
        title=file.filename,
        content=text,  # Store extracted text
        source=file.filename,
        file_type=file_ext,
        doc_type="file",  # Mark as file upload
        user_id=current_user.id
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)
    
    # Chunk Text using ingestion service
    ids, documents_content, metadatas = ingestion_service.process_text(
        text=text,
        document_id=document.id,
        title=document.title,
        doc_type="file",
        metadata={"user_id": current_user.id}
    )
    
    # Store Chunks in DB
    for i, (embedding_id, chunk_content) in enumerate(zip(ids, documents_content)):
        chunk = Chunk(
            document_id=document.id,
            chunk_index=i,
            text=chunk_content,
            embedding_id=embedding_id
        )
        db.add(chunk)
        
    await db.commit()
    
    # Add to Vector Store
    try:
        vector_store.add_documents(ids=ids, documents=documents_content, metadatas=metadatas)
    except Exception as e:
        print(f"Vector Store Error: {e}")
        # Non-blocking for now
        
    # Cleanup
    os.remove(file_path)
    
    return {"status": "success", "document_id": document.id, "chunks": len(ids)}

@router.get("/", response_model=Any)
async def get_documents(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    result = await db.execute(select(Document).where(Document.user_id == current_user.id))
    documents = result.scalars().all()
    
    # Convert to dictionaries for serialization
    result_list = []
    for doc in documents:
        result_list.append({
            "id": doc.id,
            "title": doc.title,
            "content": doc.content,
            "source": doc.source,
            "file_type": doc.file_type,
            "doc_type": doc.doc_type,
            "created_at": doc.created_at,
            "updated_at": doc.updated_at,
            "tags": doc.tags
        })
    
    return result_list

@router.delete("/{doc_id}", response_model=Any)
async def delete_document(
    doc_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    result = await db.execute(select(Document).where(Document.id == doc_id, Document.user_id == current_user.id))
    document = result.scalars().first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
        
    # Delete from Vector Store
    chunk_ids = [chunk.embedding_id for chunk in document.chunks if chunk.embedding_id]
    if chunk_ids:
        vector_store.delete(ids=chunk_ids)
        
    await db.delete(document)
    await db.commit()
    
    return {"status": "success"}

from pydantic import BaseModel

class MemoryCreate(BaseModel):
    title: str
    content: str
    tags: List[str] = []

class MemoryUpdate(BaseModel):
    title: str
    content: str
    tags: List[str] = []

@router.post("/memory", response_model=Any)
async def create_memory(
    memory_in: MemoryCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Create a new memory (replaces old document-based memory creation).
    Respects user Auto-Approve settings.
    """
    from app.models.memory import Memory
    
    # Check Auto-Approve Setting
    auto_approve = True
    user_settings = current_user.settings
    
    if user_settings:
        if isinstance(user_settings, str):
            import json
            try:
                user_settings = json.loads(user_settings)
            except:
                user_settings = {}
                
        if isinstance(user_settings, dict):
            auto_approve = user_settings.get("auto_approve", True)
        
    initial_status = "approved" if auto_approve else "pending"
    # User upload: If approved, skip inbox. If pending, show in inbox.
    show_in_inbox = True if initial_status == "pending" else False
    
    embedding_id = str(uuid.uuid4())
    
    memory = Memory(
        title=memory_in.title,
        content=memory_in.content,
        user_id=current_user.id,
        tags=memory_in.tags,
        embedding_id=embedding_id,
        status=initial_status,
        show_in_inbox=show_in_inbox,
        source_llm="user-upload" # or extension
    )
    db.add(memory)
    await db.commit()
    await db.refresh(memory)

    # Trigger Background Analysis (Auto-Tagging + Similarity)
    background_tasks.add_task(run_metadata_extraction, memory.id, current_user.id)
    
    # Ingest only if approved
    if initial_status == "approved":
        try:
            ids, documents_content, metadatas = ingestion_service.process_text(
                text=memory_in.content,
                document_id=memory.id,
                title=memory_in.title,
                doc_type="memory",
                metadata={"user_id": current_user.id, "memory_id": memory.id, "tags": str(memory_in.tags) if memory_in.tags else ""}
            )
            
            if ids:
                memory.embedding_id = ids[0]
                await db.commit()
                
                vector_store.add_documents(ids=ids, documents=documents_content, metadatas=metadatas)
        except Exception as e:
            print(f"Vector Store Error: {e}")
            
    return {"status": "success", "document_id": memory.id, "chunks": 1 if initial_status == "approved" else 0}

@router.put("/{doc_id}", response_model=Any)
async def update_document(
    doc_id: int,
    memory: MemoryUpdate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Update a document (memory only). Re-chunks and updates vector store.
    """
    # Eager load chunks to avoid lazy loading issues in async
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(Document)
        .options(selectinload(Document.chunks))
        .where(Document.id == doc_id, Document.user_id == current_user.id)
    )
    document = result.scalars().first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Update document
    document.title = memory.title
    document.content = memory.content
    document.tags = memory.tags
    
    # Delete old chunks from vector store
    # chunks are already loaded due to selectinload
    old_chunk_ids = [chunk.embedding_id for chunk in document.chunks if chunk.embedding_id]
    if old_chunk_ids:
        try:
            vector_store.delete(ids=old_chunk_ids)
        except Exception as e:
            print(f"Error deleting old chunks: {e}")
    
    # Delete old chunks from DB
    for chunk in document.chunks:
        await db.delete(chunk)
    await db.commit()
    
    # Re-chunk the updated content using ingestion service
    ids, documents_content, metadatas = ingestion_service.process_text(
        text=memory.content,
        document_id=document.id,
        title=document.title,
        doc_type=document.doc_type,
        metadata={"user_id": current_user.id, "tags": str(document.tags) if document.tags else ""}
    )
    
    # Store new chunks in DB
    for i, (embedding_id, chunk_content) in enumerate(zip(ids, documents_content)):
        chunk = Chunk(
            document_id=document.id,
            chunk_index=i,
            text=chunk_content,
            embedding_id=embedding_id
        )
        db.add(chunk)
    
    await db.commit()
    
    # Add to Vector Store
    try:
        vector_store.add_documents(ids=ids, documents=documents_content, metadatas=metadatas)
    except Exception as e:
        print(f"Vector Store Error: {e}")
    
    return {"status": "success", "document_id": document.id, "chunks": len(ids)}


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

@router.post("/search", response_model=Any)
async def search_documents(
    request: SearchRequest,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Semantic search over documents and memories.
    """
    results = vector_store.query(request.query, n_results=request.top_k, where={"user_id": current_user.id})
    
    if not results["documents"]:
        return []
        
    # Format results
    formatted_results = []
    # results["documents"] is a list of lists (one list per query)
    # results["metadatas"] is a list of lists
    
    docs = results["documents"][0]
    metas = results["metadatas"][0] if results["metadatas"] else [{}] * len(docs)
    
    for doc, meta in zip(docs, metas):
        formatted_results.append({
            "content": doc,
            "metadata": meta
        })
        
    return formatted_results


