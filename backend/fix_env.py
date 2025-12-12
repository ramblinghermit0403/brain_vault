
db_url="postgresql://postgres:Naveen1971%24@localhost:5432/brain-vault"
pinecone_host="https://brain-vault-k8ezddd.svc.aped-4627-b74a.pinecone.io"

content = f"""DATABASE_URL={db_url}
PINECONE_HOST={pinecone_host}
PINECONE_API_KEY=
OPENAI_API_KEY=
GEMINI_API_KEY=
"""

with open('.env', 'w', encoding='utf-8') as f:
    f.write(content)

print("Clean .env written.")
