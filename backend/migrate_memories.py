"""
Data Migration Script: Migrate Memory records to Document table
Run this script once to migrate existing memories to the unified Document model.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text
from app.db.session import SessionLocal
from app.core.config import settings
from app.services.vector_store import vector_store
import uuid

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200):
    """Simple text chunking function"""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def migrate_memories_to_documents():
    db = SessionLocal()
    try:
        # Check if memories table exists
        result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='memories'"))
        if not result.fetchone():
            print("No memories table found. Migration not needed.")
            return
        
        # Get all memories using raw SQL to avoid model issues
        result = db.execute(text("""
            SELECT id, user_id, title, content, embedding_id, created_at, updated_at 
            FROM memories
        """))
        memories = result.fetchall()
        
        print(f"Found {len(memories)} memories to migrate")
        
        for memory in memories:
            mem_id, user_id, title, content, embedding_id, created_at, updated_at = memory
            print(f"Migrating memory: {title}")
            
            # Insert Document using raw SQL
            db.execute(text("""
                INSERT INTO documents (user_id, title, content, source, file_type, doc_type, created_at, updated_at)
                VALUES (:user_id, :title, :content, NULL, NULL, 'memory', :created_at, :updated_at)
            """), {
                "user_id": user_id,
                "title": title,
                "content": content,
                "created_at": created_at,
                "updated_at": updated_at
            })
            
            # Get the inserted document ID
            result = db.execute(text("SELECT last_insert_rowid()"))
            document_id = result.fetchone()[0]
            
            # Chunk the content
            text_chunks = chunk_text(content)
            
            # Create chunks and add to vector store
            ids = []
            documents_content = []
            metadatas = []
            
            for i, chunk_content in enumerate(text_chunks):
                new_embedding_id = str(uuid.uuid4())
                
                # Insert chunk
                db.execute(text("""
                    INSERT INTO chunks (document_id, chunk_index, text, embedding_id, metadata_json)
                    VALUES (:document_id, :chunk_index, :text, :embedding_id, NULL)
                """), {
                    "document_id": document_id,
                    "chunk_index": i,
                    "text": chunk_content,
                    "embedding_id": new_embedding_id
                })
                
                ids.append(new_embedding_id)
                documents_content.append(chunk_content)
                metadatas.append({
                    "document_id": document_id,
                    "chunk_index": i,
                    "title": title,
                    "type": "memory"
                })
            
            # Add to vector store
            if ids:
                try:
                    vector_store.add_documents(
                        ids=ids,
                        documents=documents_content,
                        metadatas=metadatas
                    )
                    print(f"  Added {len(ids)} chunks to vector store")
                except Exception as e:
                    print(f"  Warning: Vector store error: {e}")
            
            # Delete old embedding from vector store if it exists
            if embedding_id:
                try:
                    vector_store.delete(ids=[embedding_id])
                except Exception as e:
                    print(f"  Warning: Could not delete old embedding: {e}")
        
        db.commit()
        print(f"\n✅ Migration complete! Migrated {len(memories)} memories to documents.")
        print("\nNote: The old memories table still exists. You can:")
        print("1. Keep it for backup")
        print("2. Drop it manually if you're confident: DROP TABLE memories;")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("Memory to Document Migration Script")
    print("=" * 60)
    print("\nThis will:")
    print("1. Copy all Memory records to Document table with doc_type='memory'")
    print("2. Chunk the content and create Chunk records")
    print("3. Add chunks to the vector store")
    print("4. Remove old memory embeddings from vector store")
    print("\nPress Enter to continue, or Ctrl+C to cancel...")
    
    try:
        input()
        migrate_memories_to_documents()
    except KeyboardInterrupt:
        print("\n\nMigration cancelled by user.")
        sys.exit(0)
