"""
Ingestion Service: Handle text chunking and embedding generation
"""
from typing import List, Dict
from langchain_text_splitters import RecursiveCharacterTextSplitter
import uuid
import numpy as np
import numpy as np
import os
from langchain_aws import BedrockEmbeddings
import re
import json
from app.services.llm_service import llm_service

class IngestionService:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize the ingestion service with a text splitter.
        
        Args:
            chunk_size: Maximum size of each chunk
            chunk_overlap: Number of characters to overlap between chunks
        """
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        # Initialize semantic model
        try:
            self.bedrock_embeddings = BedrockEmbeddings(
                model_id="amazon.titan-embed-text-v1",
                region_name=os.getenv("AWS_REGION", "us-east-1")
            )
        except Exception as e:
            print(f"Warning: Failed to load Bedrock embeddings: {e}")
            self.bedrock_embeddings = None
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Chunk text using RecursiveCharacterTextSplitter.
        
        Args:
            text: The text to chunk
            
        Returns:
            List of text chunks
        """
        return self.text_splitter.split_text(text)
    
    async def process_text(
        self, 
        text: str, 
        document_id: int, 
        title: str, 
        doc_type: str = "memory",
        metadata: Dict = None,
        enrich: bool = True
    ) -> tuple[List[str], List[str], List[str], List[Dict]]:
        """
        Process text into chunks with metadata for vector store.
        Uses Semantic Chunking and LLM Enrichment.
        """
        # 1. Chunking
        if len(text) < 500:
             chunks = [text] # Small enough
        else:
             chunks = self.semantic_chunk_text(text)
        
        embedding_ids = []
        chunk_texts = []
        metadatas = []
        
        base_metadata = {
            "document_id": document_id,
            "title": title,
            "type": doc_type
        }
        if metadata:
            base_metadata.update(metadata)
        
        enriched_chunk_texts = [] # Text to be embedded (contains enrichment)
        
        for i, chunk_text in enumerate(chunks):
            embedding_id = str(uuid.uuid4())
            
            embedding_ids.append(embedding_id)
            chunk_texts.append(chunk_text)
            
            chunk_metadata = base_metadata.copy()
            chunk_metadata["chunk_index"] = i
            
            # 2. Enrichment (Summary + QA)
            enriched_text = chunk_text
            
            if enrich:
                enrichment_data = await llm_service.generate_chunk_enrichment(chunk_text)
                if enrichment_data:
                    summary = enrichment_data.get("summary", "")
                    qas = enrichment_data.get("generated_qas", [])
                    entities = enrichment_data.get("entities", [])
                    
                    chunk_metadata["summary"] = summary
                    # Use json.dumps to ensure valid JSON string for Pinecone and easy parsing later
                    chunk_metadata["generated_qas"] = json.dumps(qas)
                    chunk_metadata["entities"] = json.dumps(entities)
                    
                    # Construct Enriched Text for Embedding
                    enrichment_context = f"\n\n-- Context --\nSummary: {summary}\n"
                    if qas:
                        enrichment_context += "Q&A:\n"
                        for qa in qas:
                             if isinstance(qa, dict):
                                 enrichment_context += f"Q: {qa.get('question', '')}\nA: {qa.get('answer', '')}\n"
                             elif isinstance(qa, str):
                                 enrichment_context += f"{qa}\n"
                                 
                    enriched_text += enrichment_context
            
            enriched_chunk_texts.append(enriched_text)
            metadatas.append(chunk_metadata)
        
        return embedding_ids, chunk_texts, enriched_chunk_texts, metadatas

    def semantic_chunk_text(self, text: str, threshold: float = 0.5) -> List[str]:
        """
        Split text semantically using cosine similarity of adjacent sentences.
        """
        # Split sentences
        sentences = re.split(r'(?<=[.?!])\s+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences: return []
        if len(sentences) == 1: return sentences
        
        # Encode
        try:
            # Bedrock returns list of lists (vectors)
            embeddings = self.bedrock_embeddings.embed_documents(sentences)
        except Exception as e:
            print(f"Bedrock Embedding failed: {e}")
            return self.text_splitter.split_text(text) # Fallback
            
        chunks = []
        current_chunk = [sentences[0]]
        
        for i in range(1, len(sentences)):
            # Cosine sim
            vec_a = embeddings[i-1]
            vec_b = embeddings[i]
            norm_a = np.linalg.norm(vec_a)
            norm_b = np.linalg.norm(vec_b)
            
            if norm_a == 0 or norm_b == 0:
                sim = 0
            else:
                sim = np.dot(vec_a, vec_b) / (norm_a * norm_b)
            
            if sim < threshold and len(" ".join(current_chunk)) > 150: # Check min size
                chunks.append(" ".join(current_chunk))
                current_chunk = [sentences[i]]
            else:
                # Check max size constraint (500 tokens approx 2000 chars)
                if len(" ".join(current_chunk)) + len(sentences[i]) > 2000:
                     chunks.append(" ".join(current_chunk))
                     current_chunk = [sentences[i]]
                else:
                    current_chunk.append(sentences[i])
                
        if current_chunk:
            chunks.append(" ".join(current_chunk))
            
        return chunks

    def count_tokens(self, text: str) -> int:
        """
        Estimate token count (approx 4 chars per token).
        For production, use tiktoken.
        """
        if not text:
            return 0
        return len(text) // 4

ingestion_service = IngestionService()
