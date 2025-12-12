from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.memory import Memory
from app.models.client import AIClient
from app.core.encryption import encryption_service
from app.services.llm_service import llm_service
import asyncio

class MetadataExtractionService:
    async def process_memory_metadata(self, memory_id: int, user_id: int, db: AsyncSession):
        """
        Background task to extract metadata (tags, title, summary) for a new memory.
        """
        try:
            print(f"Starting metadata extraction for memory {memory_id}")
            
            # 1. Fetch Memory
            result = await db.execute(select(Memory).where(Memory.id == memory_id))
            memory = result.scalars().first()
            if not memory:
                print(f"Memory {memory_id} not found during background task")
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
            metadata = await llm_service.extract_metadata(
                content=memory.content,
                existing_tags=existing_tags,
                api_key=api_key
            )
            print(f"Metadata Extraction: Result: {metadata}")
            
            if not metadata:
                print("LLM returned no metadata")

            # 5. Similarity / Duplicate Check
            from app.services.vector_store import vector_store
            
            try:
                # Query vector store (Sync call, should ideally be offloaded)
                sim_results = vector_store.query(
                    memory.content, 
                    n_results=2, 
                    where={"user_id": user_id}
                )
                
                similarity_data = {}
                if sim_results["documents"] and sim_results.get("distances"):
                     best_distance = sim_results["distances"][0][0]
                     best_metadata = sim_results["metadatas"][0][0] if sim_results["metadatas"] else {}
                     
                     source_id = best_metadata.get("memory_id")
                     if str(source_id) != str(memory_id):
                         if best_distance < 0.6: 
                            score = max(0, (1 - best_distance) * 100)
                            similarity_data = {
                                "score": round(score, 1),
                                "source_title": best_metadata.get("title", "Unknown"),
                                "source_id": source_id or best_metadata.get("document_id"),
                                "type": best_metadata.get("type", "memory")
                            }
                            print(f"Similarity found: {similarity_data}")
            except Exception as e:
                print(f"Similarity check failed: {e}")
                similarity_data = {}


            # 6. Update Memory
            tags_updated = False
            if metadata and metadata.get("title") and (memory.title == "Untitled" or memory.title.startswith("Memory from")):
                 print(f"Metadata Extraction: Updating title to {metadata['title']}")
                 memory.title = metadata["title"]
            
            if metadata and metadata.get("tags"):
                current_tags = memory.tags or []
                new_tags = list(set(current_tags + metadata["tags"]))
                memory.tags = new_tags
                tags_updated = True
                print(f"Metadata Extraction: Tags updated to {new_tags}")
            else:
                print("Metadata Extraction: No tags to update")
            
            if similarity_data:
                import json
                memory.task_type = json.dumps(similarity_data) 
                
                current_tags = memory.tags or []
                if "similar-content" not in current_tags:
                    new_tags = list(current_tags)
                    new_tags.append("similar-content")
                    memory.tags = new_tags

            # Commit is async
            await db.commit()
            if tags_updated:
                 print(f"Metadata Extraction: Committed changes for memory {memory_id}")
            else:
                 print(f"Metadata Extraction: Committed (No tag changes) for memory {memory_id}")
            
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
                            "id": f"mem_{memory_id}", 
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
