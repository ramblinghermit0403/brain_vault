from typing import List, Dict, Any
from app.services.vector_store import vector_store

class ContextBuilder:
    def __init__(self):
        pass

    def build_context(self, query: str, user_id: int, limit_tokens: int = 2000) -> Dict[str, Any]:
        """
        Retrieve and format context. 
        TODO: Implement advanced compression/deduplication.
        """
        # 1. Retrieve
        results = vector_store.query(query, n_results=10, where={"user_id": user_id})
        
        snippets = []
        if results["documents"]:
            snippets = results["documents"][0]
            
        # 2. Simple Format (Deduping can happen here if we had semantic checks)
        # For now, just join
        
        # 3. Truncate to limit (Approx chars)
        limit_chars = limit_tokens * 4
        current_chars = 0
        final_snippets = []
        context_text = ""
        
        for snippet in snippets:
            if current_chars + len(snippet) > limit_chars:
                break
            final_snippets.append(snippet)
            context_text += snippet + "\n\n---\n\n"
            current_chars += len(snippet)
            
        return {
            "text": context_text,
            "snippets": final_snippets,
            "token_count": int(current_chars / 4)
        }

context_builder = ContextBuilder()
