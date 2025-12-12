
import os
import sys

# Add backend to path
sys.path.append(os.getcwd())

from app.db.session import SessionLocal
from app.models.user import User
from app.services.vector_store import vector_store

def verify():
    print("--- Verifying Setup ---")
    
    # 1. DB Check
    try:
        db = SessionLocal()
        user = db.query(User).filter(User.email == "admin@brainvault.com").first()
        if user:
            print(f"[OK] Database Connected. Found Admin User: {user.email}")
        else:
            print("[FAIL] Database Connected but Admin User missing.")
    except Exception as e:
        print(f"[FAIL] Database Connection Error: {e}")
    finally:
        db.close()

    # 2. Pinecone / Vector Store Check
    try:
        print("Testing Pinecone Inference...")
        test_text = "Hello Brain Vault"
        # Test private method _get_embedding to verify inference
        embedding = vector_store._get_embedding(test_text)
        if embedding and len(embedding) > 0:
            print(f"[OK] Pinecone Inference Success. Vector Dim: {len(embedding)}")
        else:
            print("[FAIL] Pinecone returned empty embedding.")
    except Exception as e:
        print(f"[FAIL] Pinecone Error: {e}")

if __name__ == "__main__":
    verify()
