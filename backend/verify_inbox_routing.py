import requests
from app.core import security
from datetime import timedelta
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.user import User

def get_test_token():
    db = SessionLocal()
    try:
        user = db.query(User).first()
        if not user:
            print("No users found in DB. Creating one...")
            user = User(email="test@example.com", is_active=True)
            db.add(user)
            db.commit()
            db.refresh(user)
        
        user_id = user.id
        email = user.email
    finally:
        db.close()

    return security.create_access_token(
        user_id, expires_delta=timedelta(minutes=5), extra_claims={"email": email}
    )

def test_routing():
    token = get_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    base_url = "http://localhost:8000/api/v1"

    print("--- Testing LLM API (Extension Mock) ---")
    resp = requests.post(f"{base_url}/llm/save_memory", json={
        "content": "Test memory from extension LLM API",
        "source_llm": "extension", 
        "model_name": "test-model",
        "tags": ["extension"]
    }, headers=headers)
    
    if resp.status_code == 200:
        data = resp.json()
        print(f"Status: {data.get('status')} (Expected: pending)")
        if data.get('status') != 'pending':
            print("FAIL: LLM API memory was not pending.")
    else:
        print(f"Error: {resp.text}")

    print("\n--- Testing Memory API (Extension Mock via Tags) ---")
    resp = requests.post(f"{base_url}/memory/", json={
        "title": "Test Memory Ext",
        "content": "Test memory from extension popup",
        "tags": ["extension"]
    }, headers=headers)

    if resp.status_code == 200:
        data = resp.json()
        print(f"Status: {data.get('status')} (Expected: pending)")
        if data.get('status') != 'pending':
            print("FAIL: Memory API memory (with extension tag) was not pending.")
    else:
        print(f"Error: {resp.text}")

    print("\n--- Testing Memory API (Manual Mock) ---")
    # Resetting logic: Assuming auto-approve is ON for the user. 
    # If not, this might be pending too. But extension MUST be pending.
    resp = requests.post(f"{base_url}/memory/", json={
        "title": "Test Memory Manual",
        "content": "Test memory manual upload",
        "tags": ["manual"]
    }, headers=headers)

    if resp.status_code == 200:
        data = resp.json()
        print(f"Status: {data.get('status')} (Expected: approved - IF auto-approve is on)")
    else:
        print(f"Error: {resp.text}")

if __name__ == "__main__":
    test_routing()
