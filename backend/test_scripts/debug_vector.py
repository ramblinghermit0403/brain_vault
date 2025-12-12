import chromadb
from app.core.config import settings

print(f"Checking Vector Store at: {settings.CHROMA_DB_PATH}")

try:
    client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
    collection = client.get_collection(name="brain_vault_docs")
    
    count = collection.count()
    print(f"Total items in Vector Store: {count}")
    
    if count > 0:
        print("\nSample items (first 5):")
        peek = collection.peek(limit=5)
        # Peek returns a dict with lists, we iterate to show them nicely
        ids = peek['ids']
        metadatas = peek['metadatas']
        documents = peek['documents']
        
        for i in range(len(ids)):
            print(f"ID: {ids[i]}")
            print(f"Metadata: {metadatas[i]}")
            print(f"Document Snippet: {documents[i][:50]}...")
            print("-" * 20)
            
except Exception as e:
    print(f"Error accessing Vector Store: {e}")
