from app.db.session import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

def create_default_user():
    db = SessionLocal()
    try:
        if db.query(User).count() == 0:
            print("No users found. Creating default user...")
            user = User(
                email="user@example.com",
                hashed_password=get_password_hash("password"),
                is_active=True
            )
            db.add(user)
            db.commit()
            print(f"Created user: {user.email} (password: password)")
        else:
            print("User already exists.")
    finally:
        db.close()

if __name__ == "__main__":
    create_default_user()
