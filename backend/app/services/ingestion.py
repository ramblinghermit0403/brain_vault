"""
Ingestion Service: Handle text chunking and embedding generation
"""
from typing import List, Dict
from langchain_text_splitters import RecursiveCharacterTextSplitter
import uuid

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
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Chunk text using RecursiveCharacterTextSplitter.
        
        Args:
            text: The text to chunk
            
        Returns:
            List of text chunks
        """
        return self.text_splitter.split_text(text)
    
    def process_text(
        self, 
        text: str, 
        document_id: int, 
        title: str, 
        doc_type: str = "memory",
        metadata: Dict = None
    ) -> tuple[List[str], List[str], List[Dict]]:
        """
        Process text into chunks with metadata for vector store.
        
        Args:
            text: The text to process
            document_id: ID of the parent document
            title: Title of the document
            doc_type: Type of document ('memory' or 'file')
            metadata: Additional metadata to include
            
        Returns:
            Tuple of (embedding_ids, chunk_texts, metadatas)
        """
        chunks = self.chunk_text(text)
        
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
        
        for i, chunk_text in enumerate(chunks):
            embedding_id = str(uuid.uuid4())
            
            embedding_ids.append(embedding_id)
            chunk_texts.append(chunk_text)
            
            chunk_metadata = base_metadata.copy()
            chunk_metadata["chunk_index"] = i
            metadatas.append(chunk_metadata)
        
        return embedding_ids, chunk_texts, metadatas

    def count_tokens(self, text: str) -> int:
        """
        Estimate token count (approx 4 chars per token).
        For production, use tiktoken.
        """
        if not text:
            return 0
        return len(text) // 4

# Global instance
ingestion_service = IngestionService()
