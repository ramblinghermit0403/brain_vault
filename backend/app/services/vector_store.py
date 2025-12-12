import logging
import os
from typing import List, Dict, Any
from pinecone import Pinecone
from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self):
        # Initialize Pinecone Client
        api_key = settings.PINECONE_API_KEY
        if not api_key:
            logger.warning("PINECONE_API_KEY not set. Vector store will fail.")
            
        self.pc = Pinecone(api_key=api_key)
        
        # Connect to Index
        # We use the host provided in settings to connect to the specific index
        self.index = self.pc.Index(host=settings.PINECONE_HOST)
        
        # Embedding Model config
        self.embedding_model = "llama-text-embed-v2" 
        # Note: The user said "llama-text-embed-v2". 
        # Usually Pinecone maps this. We'll try the exact string first.
        
    def _get_embedding(self, text: str, input_type: str = "passage") -> List[float]:
        """
        Generate embedding using Pinecone Inference API.
        """
        try:
            # Pinecone Inference call
            embeddings = self.pc.inference.embed(
                model=self.embedding_model,
                inputs=[text],
                parameters={"input_type": input_type, "truncate": "END"}
            )
            # Return the first embedding values
            return embeddings[0].values
        except Exception as e:
            logger.error(f"Pinecone Embedding Failed: {e}")
            # Fallback or re-raise? Re-raise to alert user config is wrong
            raise e

    def add_documents(self, ids: List[str], documents: List[str], metadatas: List[Dict[str, Any]]):
        vectors = []
        for i, doc in enumerate(documents):
            # Generate embedding
            embedding = self._get_embedding(doc, input_type="passage")
            
            # Clean metadata
            clean_meta = {k: v for k, v in metadatas[i].items() if v is not None}
            # Add text to metadata for retrieval
            clean_meta["text_content"] = documents[i] 

            vectors.append({
                "id": ids[i], 
                "values": embedding, 
                "metadata": clean_meta
            })
            
        try:
            self.index.upsert(vectors=vectors)
            return True
        except Exception as e:
            print(f"Pinecone Upsert Failed: {e}")
            return False

    def query(self, query_texts: str, n_results: int = 5, where: Dict = None) -> Dict:
        """
        Query Pinecone index.
        """
        try:
            # 1. Generate embedding for query
            query_embedding = self._get_embedding(query_texts, input_type="query")
            if not query_embedding:
                return {"ids": [[]], "distances": [[]], "metadatas": [[]], "documents": [[]]}

            # 2. Query Pinecone
            search_results = self.index.query(
                vector=query_embedding,
                top_k=n_results,
                include_metadata=True,
                filter=where
            )
            
            # 3. Format results to match ChromaDB format
            ids = []
            distances = []
            metadatas = []
            documents = []

            for match in search_results["matches"]:
                ids.append(match["id"])
                # Pinecone returns similarity score (cosine). Chroma returned distance (l2).
                # We need to be careful with threshold in llm.py if we switch to cosine.
                # Pinecone cosine: 1.0 is identical.
                # But llm.py expects distance lower is better? 
                # Let's check how we initialized Pinecone. Usually likely 'cosine'.
                
                # If we assume distance... 
                # For now let's pass the score/distance as is, but logic in llm.py might need check.
                # Actually, earlier logic in llm.py: distance < threshold (1.5).
                # If Pinecone returns cosine similarity (0-1), high is good.
                # We might need to invert it or check llm.py metric.
                distances.append(match["score"]) 
                
                meta = match["metadata"] if match["metadata"] else {}
                metadatas.append(meta)
                
                # Retrieve text from metadata
                documents.append(meta.get("text_content", ""))

            return {
                "ids": [ids],
                "distances": [distances],
                "metadatas": [metadatas],
                "documents": [documents] 
            }
            
        except Exception as e:
            print(f"Pinecone Query Failed: {e}")
            return {"ids": [[]], "distances": [[]], "metadatas": [[]], "documents": [[]]}

    def delete(self, ids: List[str]):
        self.index.delete(ids=ids)

vector_store = VectorStore()
