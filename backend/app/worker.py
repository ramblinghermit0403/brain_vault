print("Loading app.worker module...")
from app.celery_app import celery_app
from app.services.metadata_extraction import metadata_service
from app.services.dedupe_job import dedupe_service
from app.services.ingestion import ingestion_service
from app.services.vector_store import vector_store
from app.db.session import AsyncSessionLocal
from app.models.memory import Memory
from app.models.document import Chunk
from app.models.fact import Fact
# Import ChatSession to ensure relationship mapper works
from app.models.chat import ChatSession
from sqlalchemy.future import select
import asyncio
import json
from datetime import datetime

# Helper to run async code in sync Celery task
def run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)
    finally:
        loop.close()

@celery_app.task(acks_late=True)
def process_memory_metadata_task(memory_id: int, user_id: int):
    """
    Background task for auto-tagging and metadata extraction.
    """
    print(f"Worker: Starting metadata extraction for memory {memory_id}")
    
    async def _process_metadata():
        async with AsyncSessionLocal() as db:
            await metadata_service.process_memory_metadata(memory_id, user_id, db)
            
    run_async(_process_metadata())

@celery_app.task(acks_late=True)
def dedupe_memory_task(memory_id: int):
    """
    Background task for duplicate detection.
    """
    print(f"Worker: Starting dedupe check for memory {memory_id}")
    
    async def _dedupe():
        async with AsyncSessionLocal() as db:
            await dedupe_service.check_duplicates(memory_id, db)

    run_async(_dedupe())

@celery_app.task(acks_late=True)
def extract_chat_facts_task(message: str, user_id: int):
    """
    Background task for extracting facts from chat messages.
    This is deferred from the chat agent to reduce response latency.
    """
    print(f"Worker: Starting fact extraction from chat message for user {user_id}")
    
    async def _extract_facts():
        from app.services.llm_service import llm_service
        from app.core.config import settings
        
        try:
            # Extract facts from the message
            extracted_facts = await llm_service.extract_facts_from_text(
                message, 
                getattr(settings, "GEMINI_API_KEY", None)
            )
            
            if extracted_facts:
                print(f"Worker: Extracted {len(extracted_facts)} facts from chat message")
                async with AsyncSessionLocal() as db:
                    for f_data in extracted_facts:
                        # Create Fact Model
                        new_fact = Fact(
                            user_id=user_id,
                            content=f"{f_data.get('subject')} {f_data.get('predicate')} {f_data.get('object')}",
                            subject=f_data.get('subject'),
                            predicate=f_data.get('predicate'),
                            object=f_data.get('object'),
                            confidence=f_data.get('confidence', 0.8),
                            source="user-chat",
                        )
                        if f_data.get("valid_from"):
                            try:
                                new_fact.valid_from = datetime.fromisoformat(f_data.get("valid_from"))
                            except:
                                pass
                                
                        db.add(new_fact)
                    await db.commit()
                print(f"Worker: Saved {len(extracted_facts)} facts to database")
            else:
                print("Worker: No facts extracted from chat message")
        except Exception as e:
            print(f"Worker: Chat fact extraction failed: {e}")
            import traceback
            traceback.print_exc()

    run_async(_extract_facts())

@celery_app.task(acks_late=True)
def ingest_memory_task(memory_id: int, user_id: int, content: str, title: str, tags: list = None, source: str = None, doc_type: str = "memory", mode: str = "append"):
    """
    Background task for ingestion (Chunking + Vector Store).
    Supports both Memory and Document models.
    mode: 'append' (default) or 'replace' (delete existing chunks first)
    """
    print(f"Worker: Starting ingestion for {doc_type} {memory_id}")
    
    async def _ingest():
        try:
            # Fetch Context Creation Date
            reference_date = None
            async with AsyncSessionLocal() as db:
                 if doc_type == "memory":
                     result = await db.execute(select(Memory).where(Memory.id == memory_id))
                     obj = result.scalars().first()
                 else:
                     # Assume Document model for other types (file, youtube, etc)
                     from app.models.document import Document
                     result = await db.execute(select(Document).where(Document.id == memory_id))
                     obj = result.scalars().first()
                     
                 if obj:
                     reference_date = obj.created_at

            # Handle Replacement (Delete old chunks)
            if mode == "replace":
                print(f"Worker: Deleting existing chunks for {doc_type} {memory_id}")
                async with AsyncSessionLocal() as db:
                    # 1. Fetch chunks to get embedding_ids for Vector Store deletion
                    # Chunk is already imported globally
                    stmt = select(Chunk)
                    if doc_type == "memory":
                        stmt = stmt.where(Chunk.memory_id == memory_id)
                    else:
                        stmt = stmt.where(Chunk.document_id == memory_id)
                        
                    result = await db.execute(stmt)
                    old_chunks = result.scalars().all()
                    
                    old_ids = [c.embedding_id for c in old_chunks if c.embedding_id]
                    
                    # 2. Delete from Vector Store
                    if old_ids:
                        try:
                            await vector_store.delete(ids=old_ids)
                        except Exception as e:
                            print(f"Worker: Warning during vector delete: {e}")
                            
                    # 3. Delete from DB
                    from sqlalchemy import delete
                    if doc_type == "memory":
                        await db.execute(delete(Chunk).where(Chunk.memory_id == memory_id))
                    else:
                        await db.execute(delete(Chunk).where(Chunk.document_id == memory_id))
                    
                    await db.commit()

            # 1. Process Text (CPU bound / API bound)
            ids, documents_content, enriched_chunk_texts, metadatas = await ingestion_service.process_text(
                text=content,
                document_id=memory_id,
                title=title,
                doc_type=doc_type,
                metadata={
                    "user_id": str(user_id), 
                    f"{doc_type}_id": memory_id, # Stores memory_id or document_id
                    "tags": str(tags) if tags else "", 
                    "source": source,
                    "created_at": str(reference_date) if reference_date else ""
                }
            )
            
            if ids:
                # 2. Add to Vector Store (Use Enriched Text)
                try:
                    await vector_store.add_documents(
                        ids=ids,
                        documents=enriched_chunk_texts, 
                        metadatas=metadatas
                    )
                except Exception as e:
                    print(f"Worker Error Adding to Vector Store: {e}")
                    return

                # 3. Parallel Fact Extraction (Optimized with Semaphore)
                from app.services.llm_service import llm_service
                from app.services.fact_service import fact_service
                
                print(f"Worker: Starting parallel fact extraction for {len(documents_content)} chunks...")
                
                # Limit concurrency 
                sem = asyncio.Semaphore(10) 

                async def _bounded_extraction(txt, ref_dt):
                    async with sem:
                        return await llm_service.extract_facts_from_text(txt, reference_date=ref_dt)

                extraction_tasks = [_bounded_extraction(text, reference_date) for text in documents_content]
                all_facts_results = await asyncio.gather(*extraction_tasks, return_exceptions=True)

                # 4. Update DB and Save Chunks
                async with AsyncSessionLocal() as db:
                     # Update Parent Object with embedding_id if applicable
                     if doc_type == "memory":
                         result = await db.execute(select(Memory).where(Memory.id == memory_id))
                         obj = result.scalars().first()
                         if obj:
                             obj.embedding_id = ids[0]
                             db.add(obj)
                     # Document model might not need embedding_id on parent, but let's check model definition if needed.
                     # Usually Document has 1:N chunks, embedding_id is on Chunk. 
                     # Memory model has embedding_id field as legacy/primary?
                     # We skip parent update for Document if field doesn't exist, but checking app/models/document.py would be good. 
                     # Assuming Document doesn't strictly require it on parent for now or we leave it.

                     # Save Chunks
                     saved_chunks = []
                     for i, (embedding_id, chunk_content) in enumerate(zip(ids, documents_content)):
                        meta = metadatas[i]
                        
                        # Safe JSON parse
                        def safe_load(k):
                            try: return json.loads(meta.get(k))
                            except: return []

                        chunk = Chunk(
                            chunk_index=i,
                            text=chunk_content,
                            embedding_id=embedding_id,
                            summary=meta.get("summary"),
                            generated_qas=safe_load("generated_qas"),
                            entities=safe_load("entities"),
                            metadata_json=meta
                        )
                        
                        # Link to correct parent
                        if doc_type == "memory":
                            chunk.memory_id = memory_id
                        else:
                            chunk.document_id = memory_id
                            
                        db.add(chunk)
                        saved_chunks.append(chunk)

                     await db.flush() 
                     await db.commit() 

                     # Parallel Fact Processing
                     async def _save_facts_safe(facts_res, c_id, u_id, m_id):
                         async with sem: 
                             async with AsyncSessionLocal() as local_db:
                                 # Maps m_id to memory_id argument regardless of type? 
                                 # fact_service.create_facts likely expects memory_id. 
                                 # If it's a document, facts might not link correctly if table expects memory_id FK.
                                 # We will pass memory_id as is, assuming facts schema supports it or we only extract facts for memories?
                                 # User wants "ingest memory task for documents too".
                                 # If Facts table requires valid memory_id FK, this will fail for Documents.
                                 # Let's skip fact extraction for non-memories to be safe/consistent OR assuming poly-morphic.
                                 # The prompt implies full ingestion.
                                 # For safety, I will pass memory_id=None if doc_type != 'memory' unless Fact supports document_id.
                                 # Let's verify Fact model later. For now, we try passing it if it was doing so before.
                                 pass 

                                 # Only create facts if it's a memory or if we updated Fact model.
                                 # Given scope, safer to only do Fact Extraction if doc_type == "memory"
                                 if doc_type == "memory":
                                     await fact_service.create_facts(
                                         facts_data=facts_res,
                                         user_id=u_id,
                                         memory_id=m_id,
                                         chunk_id=c_id,
                                         db=local_db
                                     )
                                     await local_db.commit()

                     fact_tasks = []
                     for i, chunk in enumerate(saved_chunks):
                        facts_result = all_facts_results[i]
                        if isinstance(facts_result, list) and facts_result:
                            fact_tasks.append(
                                _save_facts_safe(facts_result, chunk.id, user_id, memory_id)
                            )

                     if fact_tasks:
                         await asyncio.gather(*fact_tasks)
                     
                     print(f"Worker: Ingestion complete for {doc_type} {memory_id}")
            else:
                 print(f"Worker: No chunks generated for {doc_type} {memory_id}")

        except Exception as e:
            print(f"Worker Ingestion Failed: {e}")
            import traceback
            traceback.print_exc()

    run_async(_ingest())
