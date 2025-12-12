import asyncio
import sys
import os
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_notifications():
    print("--- Verifying Inbox Notifications ---")
    
    # Login
    login_res = requests.post(f"{BASE_URL}/auth/login", data={"username": "himanshshivhard@gmail.com", "password": "password123"})
    if login_res.status_code != 200:
        print(f"Login failed: {login_res.text}")
        return
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Enable Auto-Approve
    requests.patch(f"{BASE_URL}/user/settings", json={"auto_approve": True}, headers=headers)
    
    # 2. Create EXTERNAL memory (should be Approved + In Inbox)
    print("\n Creating External Memory (Auto-Approved)...")
    # Simulate LLM API call
    ext_res = requests.post(f"{BASE_URL}/llm/save_memory", json={
        "content": "External Notification Memory", 
        "source_llm": "chatgpt", 
        "model_name": "gpt-4"
    }, headers=headers)
    
    print(f"External Creation: {ext_res.json()}")
    ext_id = ext_res.json()["id"]
    
    # 3. Create INTERNAL memory (should be Approved + NOT In Inbox)
    print("\n Creating Internal Memory (Auto-Approved)...")
    int_res = requests.post(f"{BASE_URL}/memory/", json={
        "title": "Internal Mem",
        "content": "Internal Manual Memory"
    }, headers=headers)
    
    print(f"Internal Creation: {int_res.json()}")
    
    # 4. Check Inbox
    print("\n Checking Inbox...")
    inbox_res = requests.get(f"{BASE_URL}/inbox/", headers=headers)
    inbox = inbox_res.json()
    
    # Expect: External in inbox, Internal NOT in inbox
    ext_mem = next((m for m in inbox if m["content"] == "External Notification Memory"), None)
    int_mem = next((m for m in inbox if m["content"] == "Internal Manual Memory"), None)
    
    if ext_mem:
        print("SUCCESS: External memory found in inbox (Notification).")
        if ext_mem["status"] == "approved":
             print("SUCCESS: External memory status is 'approved'.")
        else:
             print(f"FAILURE: External memory status is {ext_mem['status']}")
    else:
        print("FAILURE: External memory NOT found in inbox.")
        
    if not int_mem:
        print("SUCCESS: Internal memory NOT found in inbox (Implicitly handled).")
    else:
        print("FAILURE: Internal memory FOUND in inbox.")
        
    # 5. Dismiss External Memory
    if ext_mem:
        print(f"\n Dismissing {ext_mem['id']}...")
        dismiss_res = requests.post(f"{BASE_URL}/inbox/{ext_mem['id']}/action", json={"action": "dismiss"}, headers=headers)
        print(f"Dismiss Result: {dismiss_res.json()}")
        
        # Check Inbox again
        inbox_final = requests.get(f"{BASE_URL}/inbox/", headers=headers).json()
        chk = next((m for m in inbox_final if m["id"] == ext_mem["id"]), None)
        if not chk:
            print("SUCCESS: Dismissed memory removed from inbox.")
            
            # Check Main Memory List (Should still exist)
            all_mem = requests.get(f"{BASE_URL}/memory/", headers=headers).json()
            # Note: Current GET /memory only returns 'approved'. Since it was auto-approved, it should be there.
            chk_main = next((m for m in all_mem if m["content"] == "External Notification Memory"), None)
            if chk_main:
                print("SUCCESS: Dismissed memory still exists in main memory.")
            else:
                 print("FAILURE: Dismissed memory disappeared from main list!")
        else:
             print("FAILURE: Dismissed memory still in inbox.")

if __name__ == "__main__":
    test_notifications()
