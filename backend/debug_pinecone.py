from app.core.config import settings
try:
    from pinecone import Pinecone
    print("Pinecone imported")
    print(f"API Key: {settings.PINECONE_API_KEY}")
    pc = Pinecone(api_key=settings.PINECONE_API_KEY)
    print("Pinecone client initialized")
except Exception as e:
    print(f"Error: {e}")
