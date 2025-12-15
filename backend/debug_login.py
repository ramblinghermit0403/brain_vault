import requests
import sys

BASE_URL = "http://localhost:8000/api/v1"

def register():
    print("Attempting Register (Mixed Case)...")
    payload = {
        "email": "MixedCase@example.com",
        "password": "password123",
        "name": "Debug User"
    }
    try:
        r = requests.post(f"{BASE_URL}/auth/register", json=payload)
        print(f"Register Status: {r.status_code}")
        print(f"Register Response: {r.text}")
    except Exception as e:
        print(f"Register Failed: {e}")

def login():
    print("\nAttempting Login (Lowercase)...")
    payload = {
        "username": "mixedcase@example.com",
        "password": "password123"
    }
    try:
        r = requests.post(f"{BASE_URL}/auth/login", data=payload)
        print(f"Login (Lower) Status: {r.status_code}")
        # print(f"Login Response: {r.text}")
    except Exception as e:
        print(f"Login (Lower) Failed: {e}")

    print("\nAttempting Login (MixedCase)...")
    # This should now work even if DB has distinct case, 
    # but wait, if DB has "MixedCase", and we search func.lower(email) == "mixedcase", it matches.
    # Our register function normalized "MixedCase@example.com" input to "mixedcase" BEFORE saving.
    # SO the DB actually has "mixedcase" for the NEW user we just created.
    # We need to manually insert a bad record to really test this, or assume existing data is bad.
    # But let's just ensure normal flow works.
    payload2 = {
        "username": "MixedCase@example.com",
        "password": "password123"
    }
    try:
        r = requests.post(f"{BASE_URL}/auth/login", data=payload2)
        print(f"Login (Mixed) Status: {r.status_code}")
    except Exception as e:
        print(f"Login (Mixed) Failed: {e}")

if __name__ == "__main__":
    register()
    login()
