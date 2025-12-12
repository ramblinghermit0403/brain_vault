import requests
import json
import secrets

BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"

def main():
    print("Starting Inbox Settings Verification...")
    
    # 1. Login or Create User
    email = f"test_settings_{secrets.token_hex(4)}@example.com"
    password = "password123"
    
    # Register
    reg_res = requests.post(f"{API_V1}/auth/register", json={"email": email, "password": password})
    if reg_res.status_code != 200:
        print(f"Failed to register: {reg_res.text}")
        return

    # Login
    login_res = requests.post(f"{BASE_URL}/api/v1/auth/login", data={"username": email, "password": password})
    if login_res.status_code != 200:
        print(f"Failed to login: {login_res.text}")
        return
        
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"Logged in as {email}")
    
    # 2. Test Default (Should be Auto-Approve = True)
    print("\n--- Testing Default Settings (Auto-Approve=True) ---")
    mem1_res = requests.post(f"{API_V1}/memory/", json={"title": "M1", "content": "Default Auto Approve"}, headers=headers)
    mem1 = mem1_res.json()
    if mem1["status"] == "approved":
        print("SUCCESS: Memory 1 auto-approved.")
    else:
        print(f"FAILURE: Memory 1 status: {mem1.get('status')}")
        
    # Check Inbox (Should be empty)
    inbox_res = requests.get(f"{API_V1}/inbox/", headers=headers)
    inbox = inbox_res.json()
    if len(inbox) == 0:
        print("SUCCESS: Inbox is empty.")
    else:
        print(f"FAILURE: Inbox has items: {len(inbox)}")
        
    # 3. Disable Auto-Approve
    print("\n--- Disabling Auto-Approve ---")
    settings_res = requests.patch(f"{API_V1}/user/settings", json={"auto_approve": False}, headers=headers)
    if settings_res.status_code == 200 and settings_res.json().get("auto_approve") is False:
        print("SUCCESS: Settings updated to False.")
    else:
        print(f"FAILURE: Settings update failed: {settings_res.text}")
        
    # 4. Create Memory (Should be Pending)
    print("\n--- Creating Pending Memory ---")
    mem2_res = requests.post(f"{API_V1}/memory/", json={"title": "M2", "content": "Pending Memory"}, headers=headers)
    mem2 = mem2_res.json()
    
    # The API response for create might return the created object. status is likely "pending".
    # But wait, create_memory returns MemorySchema.
    # If using manual SQL status, let's verify.
    if mem2["status"] == "pending": # Make sure schema exposes status? memory.py response_model=MemorySchema
        # Let's check Schema... wait, does MemorySchema have status?
        # I didn't check app/schemas/memory.py. If not, I can check inbox.
        print("SUCCESS: Memory 2 status is pending (based on response).")
    else:
        print(f"Partial Success/Failure: Response status is {mem2.get('status')}. Checking Inbox next.")
        
    # Check Inbox (Should have 1 items)
    inbox_res = requests.get(f"{API_V1}/inbox/", headers=headers)
    inbox = inbox_res.json()
    if len(inbox) == 1 and inbox[0]["content"] == "Pending Memory":
        print("SUCCESS: Memory 2 found in Inbox.")
    else:
        print(f"FAILURE: Inbox count: {len(inbox)}, Items: {inbox}")

    if len(inbox) > 0:
        # 5. Approve Memory (First Item)
        mem_id = inbox[0]["id"] # "mem_123"
        print(f"\n--- Approving {mem_id} ---")
        action_res = requests.post(f"{API_V1}/inbox/{mem_id}/action", json={"action": "approve"}, headers=headers)
        if action_res.status_code == 200 and action_res.json()["status"] == "approved":
            print("SUCCESS: Memory approved.")
        else:
            print(f"FAILURE: Approve failed: {action_res.text}")
            
    # 6. Test Discard
    print("\n--- Testing Discard Logic ---")
    mem3_res = requests.post(f"{API_V1}/memory/", json={"title": "M3", "content": "To Be Discarded"}, headers=headers)
    mem3 = mem3_res.json()
    
    # Check Inbox for M3
    inbox_res = requests.get(f"{API_V1}/inbox/", headers=headers)
    inbox = inbox_res.json()
    target_mem = next((m for m in inbox if m["content"] == "To Be Discarded"), None)
    
    if target_mem:
        print("SUCCESS: Memory 3 found in Inbox.")
        mem3_id = target_mem["id"]
        
        # Discard
        print(f"--- Discarding {mem3_id} ---")
        discard_res = requests.post(f"{API_V1}/inbox/{mem3_id}/action", json={"action": "discard"}, headers=headers)
        if discard_res.status_code == 200 and discard_res.json()["status"] == "discarded":
            print("SUCCESS: Memory discarded.")
        else:
            print(f"FAILURE: Discard failed: {discard_res.text}")
            
        # Verify NOT in Main Memory List
        print("--- Verifying Manual Memory List ---")
        main_mem_res = requests.get(f"{API_V1}/memory/", headers=headers)
        main_memories = main_mem_res.json()
        found_in_main = any(m["content"] == "To Be Discarded" for m in main_memories)
        
        if not found_in_main:
            print("SUCCESS: Discarded memory NOT in main list.")
        else:
            print("FAILURE: Discarded memory FOUND in main list.")
            
    else:
        print("FAILURE: Memory 3 not found in Inbox.")
        
    print("\nVerification Complete.")

if __name__ == "__main__":
    main()
