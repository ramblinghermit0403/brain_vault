import chromadb
from chromadb.config import Settings
from app.core.config import settings
from typing import List, Dict, Any

class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
        self.collection = self.client.get_or_create_collection(name="brain_vault_docs")

    def add_documents(self, ids: List[str], documents: List[str], metadatas: List[Dict[str, Any]]):
        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )

    def query(self, query_text: str, n_results: int = 5, where: Dict[str, Any] = None):
        return self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where=where
        )

    def delete(self, ids: List[str]):
        self.collection.delete(ids=ids)

vector_store = VectorStore()
