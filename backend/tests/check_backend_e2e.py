import httpx
import time
import sys

BASE_URL = "http://localhost:8000/api/v1"
EMAIL = "e2e_test@example.com"
PASSWORD = "password123"
NAME = "E2E Tester"

# Colors for output
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

def log(msg, success=True):
    color = GREEN if success else RED
    print(f"{color}[{'PASS' if success else 'FAIL'}]{RESET} {msg}")

def check(condition, msg, resp=None):
    if condition:
        log(msg)
    else:
        log(msg, success=False)
        if resp:
            print(f"Response Status: {resp.status_code}")
            print(f"Response Body: {resp.text}")
        sys.exit(1)

def main():
    print("Starting E2E Backend Tests...")
    
    with httpx.Client(base_url=BASE_URL, timeout=30.0) as client:
        # ---------------------------------------------------------
        # 1. Authentication
        # ---------------------------------------------------------
        print("\n--- Authentication ---")
        # Try Login
        login_payload = {"username": EMAIL, "password": PASSWORD}
        resp = client.post("/auth/login", data=login_payload)
        
        if resp.status_code == 400:
            print("User does not exist, registering...")
            reg_payload = {"email": EMAIL, "password": PASSWORD, "name": NAME}
            resp = client.post("/auth/register", json=reg_payload)
            check(resp.status_code == 200, "Registration")
            # Login again
            resp = client.post("/auth/login", data=login_payload)
        
        check(resp.status_code == 200, "Login")
        tokens = resp.json()
        access_token = tokens["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        client.headers.update(headers)
        
        # ---------------------------------------------------------
        # 2. User Settings
        # ---------------------------------------------------------
        print("\n--- User Settings ---")
        # Set Auto-Approve to True initially
        settings_payload = {"auto_approve": True}
        resp = client.patch("/user/settings", json=settings_payload)
        check(resp.status_code == 200, "Update Settings (Auto-Approve=True)")
        check(resp.json().get("auto_approve") == True, "Verify Settings Update")

        # ---------------------------------------------------------
        # 3. API Keys
        # ---------------------------------------------------------
        print("\n--- API Keys ---")
        resp = client.post("/user/api-keys", json={"name": "E2E_Test_Key"})
        check(resp.status_code == 200, "Create API Key")
        api_key_id = resp.json()["id"]
        
        resp = client.get("/user/api-keys")
        check(resp.status_code == 200, "List API Keys")
        keys = resp.json()
        check(any(k["id"] == api_key_id for k in keys), "Verify Key in List")
        
        resp = client.delete(f"/user/api-keys/{api_key_id}")
        check(resp.status_code == 200, "Revoke API Key")

        # ---------------------------------------------------------
        # 4. Memory Management (Direct)
        # ---------------------------------------------------------
        print("\n--- Memory Management ---")
        mem_payload = {
            "title": "E2E Test Memory",
            "content": "This is a test memory created by the E2E script. It contains information about Automated Testing.",
            "tags": ["e2e", "test"]
        }
        resp = client.post("/memory/", json=mem_payload)
        check(resp.status_code == 200, "Create Memory")
        memory_data = resp.json()
        memory_id = memory_data["id"]
        
        # Check Duplicate
        dup_payload = {"content": "This is a test memory created by the E2E script. It contains information about Automated Testing."}
        # Give DB a moment? Vector store might be async but check-duplicate hits it.
        # Actually check-duplicate queries vector store, which is updated via Celery. 
        # So we might not see duplicate immediately. Skipping strict duplicate check assertion, just calling endpoint.
        resp = client.post("/memory/check-duplicate", json=dup_payload)
        check(resp.status_code == 200, "Check Duplicate Endpoint")

        resp = client.get("/memory/")
        check(resp.status_code == 200, "List Memories")
        mems = resp.json()
        # ID in list is string "mem_ID" usually, looking at router
        # Let's check logic: router `read_memories` returns list of dicts with id="mem_{id}"
        found_mem = any(str(m["id"]) == f"mem_{memory_id}" for m in mems)
        check(found_mem, "Verify Memory in List")
        
        resp = client.get("/memory/tags")
        check(resp.status_code == 200, "Get Tags")
        tags = resp.json()
        check("e2e" in tags, "Verify Tag 'e2e' present")

        # ---------------------------------------------------------
        # 5. Inbox Flow
        # ---------------------------------------------------------
        print("\n--- Inbox Flow ---")
        # 1. Disable Auto-Approve
        client.patch("/user/settings", json={"auto_approve": False})
        
        # 2. Create Pending Memory
        pending_payload = {
            "title": "Pending Memory",
            "content": "This should go to inbox.",
            "tags": ["inbox-test"]
        }
        resp = client.post("/memory/", json=pending_payload)
        check(resp.status_code == 200, "Create Pending Memory")
        pending_id = resp.json()["id"] # Integer ID from schemas.Memory
        
        # 3. Check Inbox
        resp = client.get("/inbox/")
        check(resp.status_code == 200, "List Inbox")
        inbox_items = resp.json()
        # Inbox IDs are "mem_{id}"
        pending_id_str = f"mem_{pending_id}"
        check(any(i["id"] == pending_id_str for i in inbox_items), "Verify Item in Inbox")
        
        # 4. Approve
        resp = client.post(f"/inbox/{pending_id_str}/action", json={"action": "approve"})
        check(resp.status_code == 200, "Approve Inbox Item")
        
        # 5. Reset Settings
        client.patch("/user/settings", json={"auto_approve": True})

        # ---------------------------------------------------------
        # 6. Documents
        # ---------------------------------------------------------
        print("\n--- Documents ---")
        files = {'file': ('test_doc.txt', 'This is a test document content for E2E testing.', 'text/plain')}
        resp = client.post("/documents/upload", files=files)
        check(resp.status_code == 200, "Upload Document")
        doc_id = resp.json()["document_id"]
        
        resp = client.get("/documents/")
        check(resp.status_code == 200, "List Documents")
        docs = resp.json()
        check(any(d["id"] == doc_id for d in docs), "Verify Document in List")
        
        # ---------------------------------------------------------
        # 7. Search & Retrieval
        # ---------------------------------------------------------
        print("\n--- Search & Retrieval ---")
        print("Waiting 10s for background ingestion...")
        time.sleep(10) 
        
        search_payload = {"query": "Automated Testing", "top_k": 3}
        resp = client.post("/retrieval/search", json=search_payload)
        check(resp.status_code == 200, "Search Query")
        results = resp.json()
        print(f"DEBUG: Search Results: {results}")
        # Verify we found our memory
        found_text = any("Automated Testing" in r["text"] for r in results)
        check(found_text, "Verify Search Result Relevance")

        # ---------------------------------------------------------
        # 8. Chat
        # ---------------------------------------------------------
        print("\n--- Chat ---")
        # Create Session
        resp = client.post("/chat/sessions", json={"title": "E2E Chat"})
        check(resp.status_code == 200, "Create Chat Session")
        session_id = resp.json()["id"]
        
        # Send Message
        msg_payload = {"content": "What does the test memory say about testing?"}
        resp = client.post(f"/chat/sessions/{session_id}/message", json=msg_payload)
        check(resp.status_code == 200, "Send Chat Message", resp)
        reply = resp.json()
        print(f"Agent Reply: {reply['content'][:50]}...")
        check(len(reply["content"]) > 0, "Verify Agent Response")

        # ---------------------------------------------------------
        # 9. Prompts & LLM Utils
        # ---------------------------------------------------------
        print("\n--- Prompts & LLM ---")
        prompt_payload = {"query": "Summarize testing"}
        resp = client.post("/prompts/generate", json=prompt_payload)
        check(resp.status_code == 200, "Generate Prompt")
        
        tag_payload = {"content": "Python programming language machine learning"}
        resp = client.post("/llm/suggest_tags", json=tag_payload)
        check(resp.status_code == 200, "Suggest Tags", resp)

        # ---------------------------------------------------------
        # 10. Documents Cleanup
        # ---------------------------------------------------------
        print("\n--- Cleanup ---")
        # Delete Document
        resp = client.delete(f"/documents/{doc_id}")
        check(resp.status_code == 200, "Delete Document")
        
        # Delete Memory 1
        resp = client.delete(f"/memory/mem_{memory_id}") # Memory router handles mem_ prefix
        check(resp.status_code == 200, "Delete Memory 1")
        
        # Delete Memory 2 (Pending/Approved)
        resp = client.delete(f"/memory/mem_{pending_id}")
        check(resp.status_code == 200, "Delete Memory 2")
        
        # Delete Chat
        resp = client.delete("/chat/sessions")
        check(resp.status_code == 204, "Delete All Sessions")

        print("\n" + GREEN + "ALL TESTS PASSED!" + RESET)

if __name__ == "__main__":
    main()
