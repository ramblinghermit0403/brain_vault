import requests
import json
import secrets

BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"

def main():
    print("Starting Live Settings Debug...")
    
    # 1. Login/Reqister
    email = f"debug_live_{secrets.token_hex(4)}@example.com"
    password = "password123"
    
    requests.post(f"{API_V1}/auth/register", json={"email": email, "password": password})
    login_res = requests.post(f"{API_V1}/auth/login", data={"username": email, "password": password})
    
    if login_res.status_code != 200:
        print("Login failed")
        return
        
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"User: {email}")
    
    # 2. Get Initial Settings
    res = requests.get(f"{API_V1}/user/settings", headers=headers)
    print(f"Initial Settings: {res.json()}")
    
    # 3. Disable Auto-Approve
    print("\n--- Disabling Auto-Approve ---")
    res = requests.patch(f"{API_V1}/user/settings", json={"auto_approve": False}, headers=headers)
    print(f"PATCH Response: {res.json()}")
    
    # 4. Verify Settings persistence
    res = requests.get(f"{API_V1}/user/settings", headers=headers)
    print(f"GET Settings after patch: {res.json()}")
    
    # 5. Create Memory
    print("\n--- Creating Memory ---")
    res = requests.post(f"{API_V1}/memory/", json={"title": "Debug Mem", "content": "Should be pending"}, headers=headers)
    mem = res.json()
    print(f"Created Memory: Status={mem.get('status')}, ID={mem.get('id')}")
    
    if mem.get("status") == "pending":
        print("SUCCESS: Memory is pending.")
    else:
        print("FAILURE: Memory auto-approved despite setting.")

if __name__ == "__main__":
    main()
