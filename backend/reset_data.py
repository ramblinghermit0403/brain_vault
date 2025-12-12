import os
import shutil
from app.core.config import settings
from app.db.session import engine, SessionLocal
from app.db.base import Base
from app.models.user import User
from app.core.security import get_password_hash

def reset_data():
    print("--- Starting Data Reset ---")
    
def reset_data():
    print("--- Starting Data Reset ---")
    print(f"Target DB: {settings.DATABASE_URL}")
    
    # 1. Drop Tables (Works for both SQLite and Postgres)
    print("Dropping all tables...")
    try:
        Base.metadata.drop_all(bind=engine)
        print("Tables dropped.")
    except Exception as e:
        print(f"Error dropping tables: {e}")

    # 2. Chroma Cleanup - Removed (using Pinecone now)
    # If using Pinecone, we might want to delete index contents, but requires API key.
    # For now, we skip vector store reset in this script.

    # 3. Re-initialize Database
    print("Re-creating tables...")
    Base.metadata.create_all(bind=engine)
    
    # 4. Create Default User
    db = SessionLocal()
    try:
        user = User(
            email="admin@brainvault.com",
            hashed_password=get_password_hash("password"),
            is_active=True
        )
        db.add(user)
        db.commit()
        print("Created default user: admin@brainvault.com / password")
    except Exception as e:
        print(f"Error creating user: {e}")
    finally:
        db.close()

    print("--- Reset Complete ---")

if __name__ == "__main__":
    reset_data()
