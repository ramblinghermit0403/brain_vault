from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.memory import Memory
from app.models.cluster import MemoryCluster
from app.services.vector_store import vector_store
from app.services.websocket import manager
from app.db.session import AsyncSessionLocal
import asyncio
import json
from redis import asyncio as aioredis
from app.core.config import settings

class DedupeService:
    async def check_duplicates(self, memory_id: int, db: AsyncSession = None):
        """
        Check if a new memory is duplicate of existing ones.
        If db is provided, use it. Otherwise create a new session.
        Warning: If running in background task after request, do NOT pass request-scoped db.
        """
        if db:
            await self._process_dedupe(memory_id, db)
        else:
            async with AsyncSessionLocal() as session:
                await self._process_dedupe(memory_id, session)

    async def _publish_update(self, payload: dict, user_id: str = None):
        """
        Publish update to Redis channel for Uvicorn to broadcast.
        """
        if not settings.CELERY_BROKER_URL:
            return

        try:
            redis = aioredis.from_url(settings.CELERY_BROKER_URL)
            message = {
                "type": "message",
                "target_type": "personal" if user_id else "broadcast",
                "user_id": str(user_id) if user_id else None,
                "payload": payload
            }
            await redis.publish("brain_vault_updates", json.dumps(message))
            await redis.close()
        except Exception as e:
            print(f"Dedupe: Failed to publish Redis update: {e}")

    async def _process_dedupe(self, memory_id: int, db: AsyncSession):
        try:
            print(f"Dedupe Service: Checking duplicates for memory {memory_id}")
            # Get new memory
            from app.models.document import Document
            result = await db.execute(select(Memory).where(Memory.id == memory_id))
            memory = result.scalars().first()
            if not memory:
                return
            
            print("Dedupe: Querying vector store...")
            # Query vector store (Sync call)
            # Ensure we are not blocking if possible, but vector_store is sync for now.
            try:
                results = vector_store.query(memory.content, n_results=5, where={"user_id": memory.user_id})
                print(f"Dedupe: Vector store returned {len(results.get('ids', []))} matches")
            except Exception as vs_e:
                print(f"Dedupe: Vector store query failed: {vs_e}")
                raise vs_e
            
            best_match = None
            max_similarity = 0.0
            similar_ids = []
            
            if results["ids"]:
                for i, _ in enumerate(results["ids"][0]):
                    dist = results["distances"][0][i] if results["distances"] else 0.0
                    metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                    
                    match_id_val = metadata.get("memory_id")
                    if str(match_id_val) == str(memory_id):
                        continue
                        
                    # Pinecone returns similarity score (0-1), not distance.
                    similarity = dist * 100
                    
                    if similarity > 40: 
                        try:
                            sid = int(match_id_val)
                            similar_ids.append(sid)
                            
                            if similarity > max_similarity:
                                max_similarity = similarity
                                best_match = {
                                    "id": sid,
                                    "title": metadata.get("source_id", "Unknown ID"), 
                                    "similarity": similarity
                                }
                        except:
                            pass
                        
            if similar_ids:
                similar_ids = list(set(similar_ids))
                print(f"Dedupe: Found similar IDs: {similar_ids}")
                
                if best_match:
                    match_title = "Unknown"
                    source_type = metadata.get("type", "memory")
                    
                    try:
                        if source_type in ["document", "file"]:
                             result_doc = await db.execute(select(Document).where(Document.id == best_match["id"]))
                             existing_doc = result_doc.scalars().first()
                             if not existing_doc:
                                 print(f"Dedupe: Skipping ghost document {best_match['id']}")
                                 best_match = None
                             else:
                                 match_title = existing_doc.title
                        else:
                             result_mem = await db.execute(select(Memory).where(Memory.id == best_match["id"]))
                             existing_mem = result_mem.scalars().first()
                             if not existing_mem:
                                 print(f"Dedupe: Skipping ghost memory {best_match['id']}")
                                 best_match = None
                             else:
                                 match_title = existing_mem.title
                    except Exception as match_e:
                        print(f"Dedupe: Error fetching match: {match_e}")

                if best_match:
                    print(f"Dedupe Service: Found duplicate {max_similarity:.1f}% similar to '{match_title}'")
                    
                    similarity_data = {
                        "score": round(max_similarity, 1),
                        "source_title": match_title,
                        "source_id": best_match["id"],
                        "type": source_type
                    }
                    
                    memory.task_type = json.dumps(similarity_data)
                    
                    current_tags = memory.tags or []
                    if "similar-content" not in current_tags:
                        new_tags = list(current_tags)
                        new_tags.append("similar-content")
                        memory.tags = new_tags
                    
                    await db.commit()
                    print("Dedupe: Committed memory update")
                    
                    await self._publish_update({
                        "type": "inbox_update", 
                        "id": f"mem_{memory.id}", 
                        "action": "analyzed"
                    })

                # Create Cluster
                if similar_ids:
                    cluster = MemoryCluster(
                        user_id=memory.user_id,
                        memory_ids=json.dumps(similar_ids + [memory.id]),
                        representative_text=f"Cluster centered on: {memory.title}",
                        status="pending"
                    )
                    db.add(cluster)
                    await db.commit()
                    print("Dedupe: Committed cluster")
                    
                    if memory.user_id:
                        await self._publish_update({
                            "type": "new_cluster", 
                            "cluster_id": cluster.id,
                            "count": len(similar_ids) + 1
                        }, user_id=str(memory.user_id))
                    
        except Exception as e:
            print(f"Dedupe job failed: {e}")

    async def run_periodic_check(self, db_session_factory):
        """
        Periodically run dedupe checks or other background maintenance.
        """
        while True:
            try:
                await asyncio.sleep(60) 
            except Exception as e:
                print(f"Background job error: {e}")
                await asyncio.sleep(60)

dedupe_service = DedupeService()
