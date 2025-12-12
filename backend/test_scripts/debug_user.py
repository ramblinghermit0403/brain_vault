import sys
import os

# Add backend to path (parent of current script directory's parent)
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.db.session import SessionLocal
from app.models.user import User

db = SessionLocal()
try:
    user = db.query(User).first()
    if user:
        print(f"User Found: {user.email}")
        print(f"Settings (Raw): {user.settings}")
        print(f"Settings Type: {type(user.settings)}")
    else:
        print("No user found.")
finally:
    db.close()
