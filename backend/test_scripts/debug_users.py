from app.db.session import SessionLocal
from app.models.user import User

def list_users():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        print(f"Total Users: {len(users)}")
        for user in users:
            print(f"ID: {user.id} | Email: {user.email}")
    finally:
        db.close()

if __name__ == "__main__":
    list_users()
