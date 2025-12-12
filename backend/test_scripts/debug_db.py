from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.user import User
from app.models.memory import Memory

# Setup DB connection
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

print("--- Debugging Database ---")

# Check Users
users = session.query(User).all()
print(f"Total Users: {len(users)}")
for user in users:
    print(f"User ID: {user.id}, Email: {user.email}")

# Check Memories
memories = session.query(Memory).all()
print(f"\nTotal Memories: {len(memories)}")
for memory in memories:
    print(f"Memory ID: {memory.id}, User ID: {memory.user_id}, Title: {memory.title}")

session.close()
