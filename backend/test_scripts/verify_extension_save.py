import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_extension_save():
    print("--- Verifying Extension Save Logic ---")
    
    # Login
    login_res = requests.post(f"{BASE_URL}/auth/login", data={"username": "himanshshivhard@gmail.com", "password": "password123"})
    if login_res.status_code != 200:
        print(f"Login failed: {login_res.text}")
        return
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Simulate Extension Request (POST /memory/ with tag)
    print("Simulating Extension Save...")
    payload = {
        "title": "Extension Test Clip",
        "content": "Content captured from browser extension",
        "tags": ["extension"]
    }
    
    res = requests.post(f"{BASE_URL}/memory/", json=payload, headers=headers)
    print(f"Response: {res.status_code} - {res.text}")
    
    if res.status_code != 200:
        print("FAILURE: Save failed")
        return

    mem_data = res.json()
    
    # Check Inbox
    print("Checking Inbox...")
    inbox_res = requests.get(f"{BASE_URL}/inbox/", headers=headers)
    inbox = inbox_res.json()
    
    found = next((i for i in inbox if i["details"] == "Extension Test Clip"), None)
    
    if found:
        print("SUCCESS: Found in Inbox as Notification.")
        if found["status"] == "approved":
             print("SUCCESS: Status is Approved (Notification Mode).")
    else:
        print("FAILURE: Not found in Inbox.")

if __name__ == "__main__":
    test_extension_save()
