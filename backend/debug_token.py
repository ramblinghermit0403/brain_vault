from app.core import security
from datetime import timedelta
from app.core.config import settings
from jose import jwt

def test_token_creation():
    user_id = 1
    user_email = "test@example.com"
    expires = timedelta(minutes=15)
    
    # Simulate the call from auth.py
    token = security.create_access_token(
        user_id, expires_delta=expires, extra_claims={"email": user_email}
    )
    
    # Decode it
    decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    print(f"Decoded Token Payload: {decoded}")
    
    if "email" in decoded and decoded["email"] == user_email:
        print("SUCCESS: Email is in the token.")
    else:
        print("FAILURE: Email is MISSING from the token.")

if __name__ == "__main__":
    test_token_creation()
