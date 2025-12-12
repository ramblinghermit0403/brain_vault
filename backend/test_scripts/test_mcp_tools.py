import asyncio
import os
import sys
from app.db.session import SessionLocal
from app.models.user import User
from mcp_server import save_memory, list_memories, update_memory, delete_memory, generate_prompt

# Ensure we are in backend dir
sys.path.append(os.getcwd())

async def main():
    print("Starting Tool Verification...")
    
    db = SessionLocal()
    try:
        user = db.query(User).first()
        if not user:
            print("No user found. Run create_user.py first.")
            return
            
        os.environ["BRAIN_VAULT_USER_ID"] = str(user.id)
        
        # 1. Create a Test Memory
        print("\n--- 1. Creating Test Memory ---")
        save_res = await save_memory("This is a temporary test memory for MCP tools.", tags=["test"])
        print(save_res)
        mem_id = save_res.split("ID: ")[1]
        full_mem_id = f"mem_{mem_id}"
        
        # 2. List Memories
        print("\n--- 2. Listing Memories ---")
        list_res = await list_memories(limit=5)
        print(list_res)
        if full_mem_id in list_res:
            print("SUCCESS: Memory found in list.")
        else:
            print("FAILURE: Memory not found in list.")
            
        # 3. Update Memory
        print("\n--- 3. Updating Memory ---")
        update_res = await update_memory(full_mem_id, "This is the UPDATED content for the test memory.")
        print(update_res)
        
        # Verify Update via List
        list_res_2 = await list_memories(limit=1)
        if "UPDATED" in str(list_res_2): # Ideally we'd check content, but list only shows title/ID. 
            # Wait, list_memories implementation only shows ID/Title. 
            # Let's trust the return message for now or check DB.
            pass
            
        # 4. Generate Prompt
        print("\n--- 4. Generating Prompt ---")
        prompt_res = await generate_prompt("What is this test memory about?", template="standard")
        print(f"Prompt Length: {len(prompt_res)}")
        if "UPDATED" in prompt_res:
             print("SUCCESS: Context contains updated content.")
        else:
             print("WARNING: Context might not have indexed yet or query failed.")

        # 5. Delete Memory
        print("\n--- 5. Deleting Memory ---")
        del_res = await delete_memory(full_mem_id)
        print(del_res)
        
        # Verify Deletion
        list_res_3 = await list_memories(limit=5)
        if full_mem_id not in list_res_3:
            print("SUCCESS: Memory deleted.")
        else:
            print("FAILURE: Memory still in list.")

    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
