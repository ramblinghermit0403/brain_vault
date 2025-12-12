from app.db.session import SessionLocal
from app.models.document import Document
from app.models.user import User

def list_latest_docs():
    db = SessionLocal()
    try:
        docs = db.query(Document).order_by(Document.created_at.desc()).limit(5).all()
        print(f"Latest 5 Documents:")
        for doc in docs:
            user = db.query(User).get(doc.user_id)
            print(f"ID: {doc.id} | User: {user.email} | Title: {doc.title} | Content: {doc.content[:30]}...")
    finally:
        db.close()

if __name__ == "__main__":
    list_latest_docs()
