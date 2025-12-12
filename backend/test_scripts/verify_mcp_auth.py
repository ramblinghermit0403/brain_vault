import asyncio
import os
import sys
from app.db.session import SessionLocal
from app.models.user import User
from app.models.document import Document
from mcp_server import save_memory, search_memory, get_document

# Ensure we are in backend dir
sys.path.append(os.getcwd())

async def main():
    print("Starting Verification...")
    
    db = SessionLocal()
    try:
        # 1. Setup Test Users
        user1 = db.query(User).filter(User.email == "test1@example.com").first()
        if not user1:
            user1 = User(email="test1@example.com", hashed_password="fake")
            db.add(user1)
            db.commit()
            db.refresh(user1)
        
        user2 = db.query(User).filter(User.email == "test2@example.com").first()
        if not user2:
            user2 = User(email="test2@example.com", hashed_password="fake")
            db.add(user2)
            db.commit()
            db.refresh(user2)
            
        print(f"User 1 ID: {user1.id}")
        print(f"User 2 ID: {user2.id}")
        
        # 2. Test Save Memory as User 1
        print("\n--- Testing Save Memory (User 1) ---")
        os.environ["BRAIN_VAULT_USER_ID"] = str(user1.id)
        res = await save_memory("Secret plan for world domination by User 1", tags=["secret"])
        print(f"Save Result: {res}")
        
        if "ID: " not in res:
            print("ERROR: Could not find ID in save result.")
            return

        # Extract Doc ID
        doc_id = int(res.split("ID: ")[1])
        
        # 3. Test Search Memory as User 1 (Should find it)
        print("\n--- Testing Search Memory (User 1) ---")
        search_res = await search_memory("world domination")
        print(f"Search Result (User 1):\n{search_res}")
        if "Secret plan" in search_res:
            print("SUCCESS: User 1 found their memory.")
        else:
            print("FAILURE: User 1 did not find their memory.")

        # 4. Test Search Memory as User 2 (Should NOT find it)
        print("\n--- Testing Search Memory (User 2) ---")
        os.environ["BRAIN_VAULT_USER_ID"] = str(user2.id)
        search_res_2 = await search_memory("world domination")
        print(f"Search Result (User 2):\n{search_res_2}")
        if "No relevant memories found" in search_res_2:
            print("SUCCESS: User 2 did not find User 1's memory.")
        else:
            print("FAILURE: User 2 found User 1's memory!")

        # 5. Test Get Document as User 2 (Should fail)
        print("\n--- Testing Get Document (User 2 accessing User 1 doc) ---")
        get_res = await get_document(doc_id)
        print(f"Get Document Result: {get_res}")
        if "Access Denied" in get_res:
            print("SUCCESS: Access Denied for User 2.")
        else:
            print("FAILURE: User 2 accessed User 1's document!")

    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
