import asyncio
from app.db.session import SessionLocal
from app.services.vector_store import vector_store
from app.services.ingestion import ingestion_service
from app.services.dedupe_job import dedupe_service
from app.models.memory import Memory
from app.models.user import User

def test_isolation():
    print("\n--- Testing Vector Store Isolation ---")
    
    # 1. Create Data
    user1_id = 1
    user2_id = 2
    
    # Ingest for User 1
    ids1, chunks1, meta1 = ingestion_service.process_text(
        text="Secret of User 1", document_id=101, title="User 1 Doc", doc_type="memory",
        metadata={"user_id": user1_id, "memory_id": 101}
    )
    vector_store.add_documents(ids1, chunks1, meta1)
    
    # Ingest for User 2
    ids2, chunks2, meta2 = ingestion_service.process_text(
        text="Secret of User 2", document_id=102, title="User 2 Doc", doc_type="memory",
        metadata={"user_id": user2_id, "memory_id": 102}
    )
    vector_store.add_documents(ids2, chunks2, meta2)
    
    # 2. Query as User 1
    results1 = vector_store.query("Secret", n_results=5, where={"user_id": user1_id})
    print(f"User 1 Search Results: {len(results1['ids'][0])}")
    for meta in results1['metadatas'][0]:
        print(f" - Found Doc ID: {meta.get('document_id')} | User ID: {meta.get('user_id')}")
        if meta.get('user_id') != user1_id:
            print("❌ FAILURE: User 1 saw User 2's data!")

    # 3. Query as User 2
    results2 = vector_store.query("Secret", n_results=5, where={"user_id": user2_id})
    print(f"User 2 Search Results: {len(results2['ids'][0])}")
    
    # Cleanup
    vector_store.delete(ids=ids1 + ids2)

def test_dedupe_logic():
    print("\n--- Testing Dedupe Logic IDs ---")
    # Simulate return from Chroma
    # Chroma returns IDs (UUIDs) and Metadatas
    
    mock_id = "mem_123" # This is wrong, Chroma IDs are UUIDs from ingestion.py
    
    # Real ingestion produces UUIDs
    ids, _, metadatas = ingestion_service.process_text("test", 1, "t", "m", {"memory_id": 123})
    print(f"Generated Vector ID: {ids[0]}")
    print(f"Generated Metadata: {metadatas[0]}")
    
    # The dedupe job iterates results['ids'][0].
    # But IngestionService sets ID to UUID. 
    # So dedupe_job.py doing `if sid.startswith("mem_")` will FAIL.
    # It must look at metadata['memory_id'].

if __name__ == "__main__":
    test_isolation()
    test_dedupe_logic()
