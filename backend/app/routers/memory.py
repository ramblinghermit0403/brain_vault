from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid

from app.api import deps
from app.models.user import User
from app.models.memory import Memory
from app.schemas.memory import Memory as MemorySchema, MemoryCreate, MemoryUpdate
from app.services.vector_store import vector_store

router = APIRouter()

@router.post("/", response_model=MemorySchema)
def create_memory(
    memory_in: MemoryCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Create new memory.
    """
    print(f"Creating memory for user: {current_user.id}")
    print(f"Memory data: {memory_in}")
    
    # Generate embedding ID
    embedding_id = str(uuid.uuid4())
    
    memory = Memory(
        title=memory_in.title,
        content=memory_in.content,
        user_id=current_user.id,
        embedding_id=embedding_id
    )
    db.add(memory)
    try:
        db.commit()
        print("Memory committed to DB")
    except Exception as e:
        print(f"Error committing to DB: {e}")
        db.rollback()
        raise e
        
    db.refresh(memory)
    print(f"Memory ID: {memory.id}")
    
    # Add to Vector DB
    try:
        vector_store.add_documents(
            ids=[embedding_id],
            documents=[memory_in.content],
            metadatas=[{"memory_id": memory.id, "type": "memory", "title": memory_in.title, "user_id": current_user.id}]
        )
        print("Memory added to Vector Store")
    except Exception as e:
        print(f"Error adding to Vector Store: {e}")
        # We might want to rollback DB here or just log error
    
    return memory

from app.models.document import Document

@router.get("/", response_model=List[MemorySchema])
def read_memories(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Retrieve memories and documents.
    """
    # Fetch Memories
    memories = db.query(Memory).filter(Memory.user_id == current_user.id).all()
    
    # Fetch Documents
    documents = db.query(Document).filter(Document.user_id == current_user.id).all()
    
    results = []
    
    for mem in memories:
        results.append({
            "id": f"mem_{mem.id}",
            "title": mem.title,
            "content": mem.content,
            "user_id": mem.user_id,
            "created_at": mem.created_at,
            "updated_at": mem.updated_at,
            "type": "memory"
        })
        
    for doc in documents:
        results.append({
            "id": f"doc_{doc.id}",
            "title": doc.title,
            "content": f"Uploaded Document: {doc.source} ({doc.file_type})",
            "user_id": doc.user_id,
            "created_at": doc.created_at,
            "updated_at": None,
            "type": "document"
        })
    
    # Sort by created_at desc
    results.sort(key=lambda x: x["created_at"], reverse=True)
    
    # Apply pagination
    return results[skip : skip + limit]

@router.put("/{memory_id}", response_model=MemorySchema)
def update_memory(
    memory_id: str,
    memory_in: MemoryUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Update a memory.
    """
    if memory_id.startswith("doc_"):
        raise HTTPException(status_code=400, detail="Cannot edit documents via memory editor")
        
    real_id = int(memory_id.split("_")[1])
    
    memory = db.query(Memory).filter(Memory.id == real_id, Memory.user_id == current_user.id).first()
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    
    memory.title = memory_in.title
    memory.content = memory_in.content
    db.commit()
    db.refresh(memory)
    
    # Update Vector DB (Delete old, add new)
    if memory.embedding_id:
        vector_store.delete(ids=[memory.embedding_id])
    
    vector_store.add_documents(
        ids=[memory.embedding_id],
        documents=[memory.content],
        metadatas=[{"memory_id": memory.id, "type": "memory", "title": memory.title, "user_id": current_user.id}]
    )
    
    # Return with prefix
    return {
        "id": f"mem_{memory.id}",
        "title": memory.title,
        "content": memory.content,
        "user_id": memory.user_id,
        "created_at": memory.created_at,
        "updated_at": memory.updated_at,
        "type": "memory"
    }

@router.delete("/{memory_id}", response_model=Any)
def delete_memory(
    memory_id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Delete a memory or document.
    """
    if memory_id.startswith("doc_"):
        # Handle Document Deletion
        doc_id = int(memory_id.split("_")[1])
        document = db.query(Document).filter(Document.id == doc_id, Document.user_id == current_user.id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Delete chunks from vector store?
        # We need to find chunks associated with this doc. 
        # The vector store delete by ID might be tricky if we don't have embedding IDs handy.
        # But our Document model has chunks relationship.
        
        for chunk in document.chunks:
            if chunk.embedding_id:
                vector_store.delete(ids=[chunk.embedding_id])
        
        db.delete(document)
        db.commit()
        return {"status": "success", "id": memory_id}
        
    elif memory_id.startswith("mem_"):
        # Handle Memory Deletion
        mem_id = int(memory_id.split("_")[1])
        memory = db.query(Memory).filter(Memory.id == mem_id, Memory.user_id == current_user.id).first()
        if not memory:
            raise HTTPException(status_code=404, detail="Memory not found")
        
        if memory.embedding_id:
            vector_store.delete(ids=[memory.embedding_id])
            
        db.delete(memory)
        db.commit()
        return {"status": "success", "id": memory_id}
    
    else:
        # Fallback for old int IDs if any
        try:
            mem_id = int(memory_id)
            memory = db.query(Memory).filter(Memory.id == mem_id, Memory.user_id == current_user.id).first()
            if not memory:
                raise HTTPException(status_code=404, detail="Memory not found")
            if memory.embedding_id:
                vector_store.delete(ids=[memory.embedding_id])
            db.delete(memory)
            db.commit()
            return {"status": "success", "id": memory_id}
        except ValueError:
             raise HTTPException(status_code=400, detail="Invalid ID format")
