import requests
import json
import sqlite3

BASE_URL = "http://localhost:8000/api/v1"

def test_auto_approve():
    print("--- Verifying Auto-Approve Logic ---")
    
    # Login
    login_res = requests.post(f"{BASE_URL}/auth/login", data={"username": "himanshshivhard@gmail.com", "password": "password123"})
    if login_res.status_code != 200:
        print(f"Login failed: {login_res.text}")
        return
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Disable Auto-Approve
    print("Disabling Auto-Approve...")
    requests.patch(f"{BASE_URL}/user/settings", json={"auto_approve": False}, headers=headers)
    
    # 2. Check Settings API
    settings_res = requests.get(f"{BASE_URL}/user/settings", headers=headers)
    print(f"Settings API Response: {settings_res.json()}")
    
    # 3. Create Memory
    print("Creating Memory via LLM API...")
    res = requests.post(f"{BASE_URL}/llm/save_memory", json={
        "content": "Test Pending Memory", 
        "source_llm": "test_script", 
        "model_name": "test"
    }, headers=headers)
    
    mem_data = res.json()
    print(f"Creation Response: {mem_data}")
    
    if mem_data["status"] == "pending":
        print("SUCCESS: Memory is pending.")
    else:
        print(f"FAILURE: Memory is {mem_data['status']} (Expected pending).")
        
    # 4. Check Inbox (Should be visible)
    inbox_res = requests.get(f"{BASE_URL}/inbox/", headers=headers)
    inbox_items = inbox_res.json()
    found = any(i["content"] == "Test Pending Memory" for i in inbox_items)
    
    if found:
         print("SUCCESS: Found in Inbox.")
    else:
         print("FAILURE: NOT found in Inbox.")

    # 5. Check Main Memory List (Should NOT be visible)
    mem_res = requests.get(f"{BASE_URL}/memory/", headers=headers)
    mems = mem_res.json()
    found_main = any(m["content"] == "Test Pending Memory" for m in mems)
    
    if found_main:
        print("FAILURE: Found in Main Memory List (Should be hidden).")
    else:
        print("SUCCESS: Not in Main Memory List.")

if __name__ == "__main__":
    test_auto_approve()
