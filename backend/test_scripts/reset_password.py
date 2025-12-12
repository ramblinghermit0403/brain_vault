import sys
import os

# Add backend to path (parent of current script directory's parent)
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.db.session import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

db = SessionLocal()
try:
    user = db.query(User).first()
    if user:
        print(f"Resetting password for {user.email}")
        user.hashed_password = get_password_hash("password123")
        db.commit()
        print("Password reset to 'password123'")
    else:
        print("No user found")
finally:
    db.close()
