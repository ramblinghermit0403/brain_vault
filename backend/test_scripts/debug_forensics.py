import os
from app.db.session import SessionLocal
from app.models.user import User
from app.models.memory import Memory

def get_mcp_resolved_user(db):
    # Logic copied from mcp_server.py
    user_email = os.environ.get("BRAIN_VAULT_USER_EMAIL")
    if user_email:
        return db.query(User).filter(User.email == user_email).first(), "Env Var (Email)"
            
    user_id = os.environ.get("BRAIN_VAULT_USER_ID")
    if user_id:
        return db.query(User).filter(User.id == int(user_id)).first(), "Env Var (ID)"
            
    return db.query(User).first(), "Fallback (First User)"

def analyze():
    db = SessionLocal()
    try:
        print("\n--- MCP SERVER USER RESOLUTION ---")
        resolved_user, method = get_mcp_resolved_user(db)
        if resolved_user:
            print(f"MCP Server currently resolves to: {resolved_user.email} (ID: {resolved_user.id})")
            print(f"Resolution Method: {method}")
        else:
            print("MCP Server resolves to: NONE")

        print("\n--- PENDING MEMORIES IN DB ---")
        memories = db.query(Memory).filter(Memory.status == "pending").all()
        if not memories:
            print("No pending memories found.")
        else:
            for mem in memories:
                owner = db.query(User).get(mem.user_id)
                print(f"Memory ID: {mem.id} | Title: {mem.title} | Owner: {owner.email} (ID: {mem.user_id})")

        print("\n--- ALL USERS ---")
        users = db.query(User).all()
        for u in users:
            print(f"ID: {u.id} | Email: {u.email}")
            
    finally:
        db.close()

if __name__ == "__main__":
    analyze()
