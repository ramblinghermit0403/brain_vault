from app.db.session import SessionLocal
from app.models.memory import Memory
from app.models.user import User

def list_latest_memories():
    db = SessionLocal()
    try:
        memories = db.query(Memory).order_by(Memory.created_at.desc()).limit(5).all()
        print(f"Latest 5 Memories:")
        for mem in memories:
            user = db.query(User).get(mem.user_id)
            print(f"ID: {mem.id} | User: {user.email} | Status: {mem.status} | Source: {mem.source_llm} | Content: {mem.content[:30]}...")
    finally:
        db.close()

if __name__ == "__main__":
    list_latest_memories()
