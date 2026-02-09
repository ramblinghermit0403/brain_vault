import uuid
import json
from typing import List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.memory import Memory
from app.models.user import User
from app.worker import process_memory_metadata_task, ingest_memory_task, dedupe_memory_task

class MemoryService:
    async def create_memory(
        self,
        db: AsyncSession,
        user: User,
        content: str,
        title: Optional[str] = None,
        source: str = "user",
        tags: Optional[List[str]] = None,
        created_at: Optional[Any] = None 
    ) -> Memory:
        """
        Create a new memory and trigger background processing tasks.
        """
        print(f"MemoryService: Creating memory for user: {user.id}")
        
        # Default title if not provided
        if not title:
            title = f"Memory from {source}"

        # Generate embedding ID
        embedding_id = str(uuid.uuid4())
        
        # Check Auto-Approve Setting
        auto_approve = True
        user_settings = user.settings
        
        if user_settings:
            if isinstance(user_settings, str):
                try:
                    user_settings = json.loads(user_settings)
                except:
                    user_settings = {}
                    
            if isinstance(user_settings, dict):
                auto_approve = user_settings.get("auto_approve", True)
                
        initial_status = "approved" if auto_approve else "pending"
        
        # Logic for inbox visibility
        # Rule: Only external sources (extension, agent_drop, mcp) should go to inbox
        # Memories created from within the app (web-app, user) should NEVER go to inbox
        tags_list = tags or []
        is_extension = "extension" in tags_list
        is_external_source = source in ["extension", "agent_drop", "mcp", "browser_extension"]
        
        # Only show in inbox if from external source OR if pending and from external
        show_in_inbox = is_external_source or is_extension
        
        # If auto-approved and not external, definitely skip inbox
        if initial_status == "approved" and not is_external_source and not is_extension:
            show_in_inbox = False
            
        memory = Memory(
            title=title,
            content=content,
            user_id=user.id,
            tags=tags_list,
            embedding_id=embedding_id,
            status=initial_status,
            show_in_inbox=show_in_inbox,
            source_llm=source
        )
        
        # Handle backdating (e.g. for MemoryBench or imports)
        normalized_tags = [t.lower() for t in tags_list]
        if "memorybench" in normalized_tags and created_at:
            print(f"Applying MemoryBench backdate: {created_at}")
            memory.created_at = created_at
        elif created_at:
             memory.created_at = created_at
            
        db.add(memory)
        try:
            await db.commit()
            print("Memory committed to DB")
        except Exception as e:
            print(f"Error committing to DB: {e}")
            await db.rollback()
            raise e
            
        await db.refresh(memory)
        print(f"Memory ID: {memory.id}")
        
        # Trigger Background Tasks
        # 1. Metadata / Auto-Tagging
        process_memory_metadata_task.delay(memory.id, user.id)
        
        # 2. Ingestion (Vector DB)
        if initial_status == "approved":
            ingest_memory_task.delay(
                memory.id,
                user.id,
                content,
                title,
                tags_list,
                source
            )

        # 3. Deduplication Check
        dedupe_memory_task.delay(memory.id)
        
        return memory

memory_service = MemoryService()
