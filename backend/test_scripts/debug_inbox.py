from app.db.session import SessionLocal
from app.models.memory import Memory
from app.models.user import User

def list_pending_all():
    db = SessionLocal()
    try:
        memories = db.query(Memory).filter(Memory.status == "pending").all()
        print(f"Total Pending Memories: {len(memories)}")
        for mem in memories:
            user = db.query(User).get(mem.user_id)
            print(f"Memory ID: {mem.id} | User: {user.email} (ID: {mem.user_id}) | Title: {mem.title} | Source: {mem.source_llm}")
    finally:
        db.close()

if __name__ == "__main__":
    list_pending_all()
