from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.memory import Memory
from app.models.client import AIClient
from app.core.encryption import encryption_service
from app.services.llm_service import llm_service
import asyncio

from app.models.document import Document

class MetadataExtractionService:
    async def process_memory_metadata(self, memory_id: int, user_id: int, db: AsyncSession, doc_type: str = "memory"):
        """
        Background task to extract metadata (tags, title, summary) for a new memory or document.
        """
        try:
            print(f"Starting metadata extraction for {doc_type} {memory_id}")
            
            # 1. Fetch Record
            if doc_type == "memory":
                result = await db.execute(select(Memory).where(Memory.id == memory_id))
                record = result.scalars().first()
            else:
                result = await db.execute(select(Document).where(Document.id == memory_id))
                record = result.scalars().first()
                
            if not record:
                print(f"{doc_type} {memory_id} not found during background task")
                return

            # 2. Fetch User Keys (Try Gemini first (fast/cheap), then OpenAI)
            provider = "gemini" 
            result = await db.execute(select(AIClient).where(
                AIClient.user_id == user_id, 
                AIClient.provider == provider
            ))
            client = result.scalars().first()
            
            if not client:
                 # Fallback to openai
                 provider = "openai"
                 result = await db.execute(select(AIClient).where(
                    AIClient.user_id == user_id, 
                    AIClient.provider == provider
                ))
                 client = result.scalars().first()
            
            api_key = None
            if client:
                try:
                    api_key = encryption_service.decrypt(client.encrypted_api_key)
                except Exception as e:
                    print(f"Failed to decrypt key: {e}")

            if not api_key:
                print("No suitable API key found for metadata extraction")
                return

            print(f"Metadata Extraction: Using provider {provider} for user {user_id}")

            # 3. Get Existing Tags (for context)
            existing_tags = []
            try:
                result = await db.execute(select(Memory.tags).where(Memory.user_id == user_id).limit(100))
                all_mem_tags = result.all()
                tag_set = set()
                for m in all_mem_tags:
                    # m is a Row, likely m.tags or m[0]
                    tags_val = m.tags if hasattr(m, 'tags') else m[0]
                    if tags_val:
                        for t in tags_val:
                            tag_set.add(t)
                existing_tags = list(tag_set)
            except Exception as e:
                print(f"Error fetching existing tags: {e}")

            # 4. Call LLM Service
            print("Metadata Extraction: Calling LLM...")
            # 4. Call LLM Service
            print("Metadata Extraction: Calling LLM...")
            metadata = await llm_service.extract_metadata(
                content=record.content,
                existing_tags=existing_tags,
                api_key=api_key
            )
            print(f"Metadata Extraction: Result: {metadata}")
            
            if not metadata:
                print("LLM returned no metadata")




            # 6. Update Record
            tags_updated = False
            # Only update title if generic (Untitled)
            if metadata and metadata.get("title") and (not record.title or record.title == "Untitled" or record.title.startswith("Memory from") or record.title.startswith("scanned_")):
                 print(f"Metadata Extraction: Updating title to {metadata['title']}")
                 record.title = metadata["title"]
            
            if metadata and metadata.get("tags"):
                current_tags = record.tags or []
                new_tags = list(set(current_tags + metadata["tags"]))
                record.tags = new_tags
                tags_updated = True
                print(f"Metadata Extraction: Tags updated to {new_tags}")
            else:
                print("Metadata Extraction: No tags to update")
            
            if tags_updated:
                # Update task_type only if JSON structure required for other things, else skip
                pass

            # Commit is async
            await db.commit()
            if tags_updated:
                 print(f"Metadata Extraction: Committed changes for {doc_type} {memory_id}")
            else:
                 print(f"Metadata Extraction: Committed (No tag changes) for {doc_type} {memory_id}")
            
            # Broadcast to frontend
            # Publish update via Redis (Celery -> Uvicorn)
            try:
                from app.core.config import settings
                from redis import asyncio as aioredis
                import json
                
                if settings.CELERY_BROKER_URL:
                    redis = aioredis.from_url(settings.CELERY_BROKER_URL)
                    message = {
                        "type": "message",
                        "target_type": "broadcast",
                        "payload": {
                            "type": "inbox_update", 
                            "id": f"mem_{memory_id}" if doc_type == "memory" else f"doc_{memory_id}", 
                            "action": "analyzed"
                        }
                    }
                    await redis.publish("brain_vault_updates", json.dumps(message))
                    await redis.close()
                    print(f"Metadata Extraction: Published update to Redis")
            except Exception as redis_e:
                print(f"Metadata Extraction: Failed to publish Redis update: {redis_e}")

        except Exception as e:
            print(f"Error in process_memory_metadata: {e}")
            await db.rollback()

metadata_service = MetadataExtractionService()
