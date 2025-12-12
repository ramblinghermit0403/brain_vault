
# Force write correct config
content = """DATABASE_URL=postgresql://postgres:Denmarks123%24@localhost/brain-vault
PINECONE_HOST=https://brain-vault-k8ezddd.svc.aped-4627-b74a.pinecone.io
PINECONE_API_KEY=pcsk_3uPA8C_SAcmv2fpyunPdKgZjJ1CR5Hn4K9gG7ns9si5dVcgCEALRnURaVyG7GRYP3ZYMU6
OPENAI_API_KEY=
GEMINI_API_KEY=
"""

with open(".env", "w", encoding="utf-8") as f:
    f.write(content.strip())
    
print("Updated .env with Postgres and Pinecone credentials.")
