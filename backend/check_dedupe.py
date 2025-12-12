import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.getcwd())

from app.db.session import AsyncSessionLocal
from app.models.memory import Memory
from sqlalchemy import select, desc
from app.services.vector_store import vector_store

async def main():
    print("Connecting to DB...")
    async with AsyncSessionLocal() as db:
        # Get latest memory
        result = await db.execute(select(Memory).order_by(desc(Memory.id)).limit(1))
        memory = result.scalars().first()
        
        if not memory:
            print("No memories found in DB.")
            return

        print(f"Latest Memory: {memory.id} (User: {memory.user_id})")
        # print(f"Content Preview: {memory.content[:100]}...") # REMOVED to avoid encoding issues
        
        # Query Vector Store
        print(f"\nQuerying Pinecone WITHOUT FILTER (Debug)...")
        try:
            results = vector_store.query(memory.content, n_results=10)
            
            with open("dedupe_results.txt", "w", encoding="utf-8") as f:
                f.write(f"Latest Memory: {memory.id} (User: {memory.user_id})\n")
                
                ids = results.get("ids", [[]])[0]
                if not ids:
                    f.write("No matches found in Vector Store.\n")
                    return

                distances = results.get("distances", [[]])[0]
                metadatas = results.get("metadatas", [[]])[0]
                
                f.write(f"Found {len(ids)} matches:\n")
                
                found_duplicate = False
                for i, mid in enumerate(ids):
                    dist = distances[i]
                    meta = metadatas[i] or {}
                    similarity = (1 - dist) * 100
                    mem_id_in_meta = meta.get("memory_id")
                    is_self = str(mem_id_in_meta) == str(memory.id)
                    
                    line = f"Match {i+1}: PineconeID={mid} | MemID={mem_id_in_meta} | Sim={similarity:.2f}% | Self={is_self}\n"
                    f.write(line)
                    print(line.strip()) # Also print to show progress
                    
                    if not is_self and similarity > 40:
                        found_duplicate = True
                        f.write(f"  >>> POTENTIAL DUPLICATE FOUND: {mid}\n")
                
                if not found_duplicate:
                    f.write("\nConclusion: Logic would NOT find a duplicate (only self or low score matches).\n")
                else:
                    f.write("\nConclusion: Logic SHOULD find a duplicate.\n")

            print("Results written to dedupe_results.txt")

        except Exception as e:
            print(f"Vector Store Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
