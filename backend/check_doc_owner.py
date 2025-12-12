from app.db.session import SessionLocal
from app.models.document import Document
from app.models.user import User

db = SessionLocal()
try:
    doc = db.query(Document).filter(Document.id == 9).first()
    if doc:
        print(f"Document 9: Title='{doc.title}', UserID={doc.user_id}")
        user = db.query(User).filter(User.id == doc.user_id).first()
        print(f"Owner: {user.email if user else 'Unknown'}")
    else:
        print("Document 9 not found in DB")
        
    # Also check if there are other docs with this title
    docs = db.query(Document).filter(Document.title == "ai_brain_vault_srs.md").all()
    for d in docs:
        print(f"Found Doc: ID={d.id}, Title='{d.title}', UserID={d.user_id}")

except Exception as e:
    print(f"Error: {e}")
finally:
    db.close()
