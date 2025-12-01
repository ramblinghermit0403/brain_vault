import sys
import os
import uuid
from app.services.vector_store import vector_store
from app.services.ingestion import ingestion_service

# Ensure we are in backend dir
sys.path.append(os.getcwd())

def main():
    print("Starting App Auth Verification...")
    
    # Simulate User IDs
    user1_id = 101
    user2_id = 102
    
    # 1. Ingest Data for User 1
    print("\n--- Ingesting Data for User 1 ---")
    doc_id = 999
    text = "Top secret project details for User 1 only."
    
    ids, documents, metadatas = ingestion_service.process_text(
        text=text,
        document_id=doc_id,
        title="Secret Doc",
        doc_type="memory",
        metadata={"user_id": user1_id}
    )
    
    vector_store.add_documents(ids=ids, documents=documents, metadatas=metadatas)
    print("Data ingested.")
    
    # 2. Search as User 1 (Should find it)
    print("\n--- Searching as User 1 ---")
    results1 = vector_store.query("secret project", where={"user_id": user1_id})
    if results1["documents"] and results1["documents"][0]:
        print(f"SUCCESS: User 1 found: {results1['documents'][0][0]}")
    else:
        print("FAILURE: User 1 did not find their data.")
        
    # 3. Search as User 2 (Should NOT find it)
    print("\n--- Searching as User 2 ---")
    results2 = vector_store.query("secret project", where={"user_id": user2_id})
    if not results2["documents"] or not results2["documents"][0]:
        print("SUCCESS: User 2 found nothing.")
    else:
        print(f"FAILURE: User 2 found data: {results2['documents'][0][0]}")

    # Cleanup
    vector_store.delete(ids=ids)

if __name__ == "__main__":
    main()
