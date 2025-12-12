import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"
# Assuming we have a test user or auth disabled for testing, or we get a token.
# For simplicity, if auth is enabled, we need to login first.
# Let's assume we can use the existing test user 'test@example.com' 'password'.

def login():
    try:
        resp = requests.post(f"{BASE_URL}/auth/login", data={"username": "test@example.com", "password": "password"})
        if resp.status_code == 200:
            return resp.json()["access_token"]
        print(f"Login failed: {resp.text}")
        return None
    except Exception as e:
        print(f"Login error (Server might be down): {e}")
        return None

def verify_flow():
    token = login()
    if not token:
        print("Skipping verification due to auth failure (or server down).")
        return

    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n--- 1. Testing LLM Save Memory (Pending) ---")
    payload = {
        "content": "This is a memory from ChatGPT about Quantum Physics.",
        "source_llm": "chatgpt",
        "model_name": "gpt-4",
        "url": "https://chatgpt.com/c/123",
        "tags": ["science", "physics"]
    }
    resp = requests.post(f"{BASE_URL}/llm/save_memory", json=payload, headers=headers)
    if resp.status_code == 200:
        mem_data = resp.json()
        print(f"✅ Success: Saved memory {mem_data['id']} with status {mem_data['status']}")
        mem_id = mem_data['id']
    else:
        print(f"❌ Failed: {resp.text}")
        return

    print("\n--- 2. Testing Inbox List ---")
    resp = requests.get(f"{BASE_URL}/inbox/", headers=headers)
    inbox = resp.json()
    found = False
    for item in inbox:
        if item['id'] == mem_id:
            found = True
            print(f"✅ Success: Found memory {mem_id} in inbox.")
            break
    if not found:
        print(f"❌ Failed: Memory {mem_id} not found in inbox.")

    print("\n--- 3. Testing Inbox Action (Approve) ---")
    resp = requests.post(f"{BASE_URL}/inbox/{mem_id}/action", json={"action": "approve"}, headers=headers)
    if resp.status_code == 200:
        print(f"✅ Success: Approved memory {mem_id}.")
    else:
        print(f"❌ Failed: {resp.text}")

    print("\n--- 4. Testing Retrieve Context ---")
    resp = requests.post(f"{BASE_URL}/llm/retrieve_context", json={"query": "Quantum Physics"}, headers=headers)
    if resp.status_code == 200:
        ctx = resp.json()
        snippet_len = len(ctx['snippets'])
        print(f"✅ Success: Retrieved context with {snippet_len} snippets.")
        if snippet_len > 0:
            print("   Content snippet:", ctx['snippets'][0][:50] + "...")
    else:
        print(f"❌ Failed: {resp.text}")

if __name__ == "__main__":
    verify_flow()
