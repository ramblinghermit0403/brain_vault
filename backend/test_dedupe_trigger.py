import requests
import time
import json
import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.getcwd())

from app.core.security import create_access_token, get_password_hash
from app.db.session import AsyncSessionLocal
from app.models.user import User
from sqlalchemy.future import select

BASE_URL = "http://localhost:8000/api/v1"

async def get_or_create_token():
    async with AsyncSessionLocal() as db:
        # Check for test user
        result = await db.execute(select(User).where(User.email == "test_dedupe@bot.com"))
        user = result.scalars().first()
        
        if not user:
            print("Creating test user...")
            user = User(
                email="test_dedupe@bot.com",
                hashed_password=get_password_hash("password"),
                is_active=True
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
            print(f"Created user {user.id}")
        
        token = create_access_token(subject=user.id)
        return token

def test_dedupe():
    # 0. Auth
    try:
        if sys.platform == 'win32':
             asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        token = asyncio.run(get_or_create_token())
        headers = {"Authorization": f"Bearer {token}"}
        print(f"Got Token: {token[:10]}...")
    except Exception as e:
        print(f"Auth failed: {e}")
        return

    # 1. Create Base Memory
    print("Creating base memory...")
    title = f"Test Memory {int(time.time())}"
    content = "This is a unique test memory for deduplication logic."
    
    payload = {
        "title": title,
        "content": content,
        "tags": ["test"]
    }
    
    try:
        r = requests.post(f"{BASE_URL}/memory/", json=payload, headers=headers)
        if r.status_code != 200:
            print(f"Failed to create base memory: {r.text}")
            return
        base_id = r.json()["id"]
        print(f"Base Memory Created: {base_id}")
    except Exception as e:
        print(f"Error connecting to API: {e}")
        return

    # Wait for ingestion
    print("Waiting 3s for ingestion...")
    time.sleep(3)
    
    # 2. Create Duplicate Memory
    print("Creating duplicate memory...")
    payload_dup = {
        "title": title + " Duplicate",
        "content": content, # Same content
        "tags": ["test-dup"]
    }
    
    r = requests.post(f"{BASE_URL}/memory/", json=payload_dup, headers=headers)
    if r.status_code != 200:
        print(f"Failed to create duplicate memory: {r.text}")
        return
    dup_id = r.json()["id"]
    print(f"Duplicate Memory Created: {dup_id}")
    
    # Wait for dedupe task (Increased wait time to be safe)
    print("Waiting 15s for deduplication...")
    time.sleep(15)
    
    # 3. Check tags of duplicate
    # Fetch list
    r = requests.get(f"{BASE_URL}/memory/", headers=headers, params={"limit": 100})
    memories = r.json()
    
    # Match mem_{id}
    target_id_str = f"mem_{dup_id}"
    target_mem = next((m for m in memories if m["id"] == target_id_str), None)
    
    if target_mem:
        print(f"Target Memory Tags: {target_mem['tags']}")
        if "similar-content" in target_mem["tags"]:
            print("SUCCESS: Duplicate tag found!")
        else:
            print("FAILURE: Duplicate tag NOT found.")
            # Debug: Check base memory tags too
            base_mem = next((m for m in memories if m["id"] == base_id), None)
            if base_mem:
                 print(f"Base Memory Tags: {base_mem['tags']}")
    else:
        print("Target memory not found in list")

if __name__ == "__main__":
    test_dedupe()
