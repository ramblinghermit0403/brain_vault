from app.db.session import SessionLocal
from app.models.document import Document
from app.models.user import User

db = SessionLocal()

doc_id = 9
document = db.query(Document).filter(Document.id == doc_id).first()

if document:
    print(f"Document found: ID={document.id}, Title='{document.title}', UserID={document.user_id}, Type='{document.doc_type}'")
    user = db.query(User).filter(User.id == document.user_id).first()
    if user:
        print(f"Owner: {user.email} (ID={user.id})")
    else:
        print("Owner user not found!")
else:
    print(f"Document with ID {doc_id} not found.")

# List all documents to see what's there
print("\nAll Documents:")
docs = db.query(Document).all()
for d in docs:
    print(f"ID={d.id}, Title='{d.title}', UserID={d.user_id}")

db.close()
