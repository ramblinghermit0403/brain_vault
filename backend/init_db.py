from app.db.base import Base
from app.db.session import engine
from app.models.user import User
from app.models.document import Document
from app.models.memory import Memory
from app.models.client import AIClient
from app.models.history import MemoryHistory
from app.models.audit import AuditLog
from app.models.cluster import MemoryCluster

def init_db():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

if __name__ == "__main__":
    init_db()
