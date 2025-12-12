import os

new_url = "postgresql://postgres:Denmarks123%24@localhost/brain-vault"
env_path = ".env"

if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    new_lines = []
    url_found = False
    for line in lines:
        if line.startswith("DATABASE_URL="):
            new_lines.append(f"DATABASE_URL={new_url}\n")
            url_found = True
        else:
            new_lines.append(line)
    
    if not url_found:
        new_lines.append(f"DATABASE_URL={new_url}\n")
        
    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    print("Updated DATABASE_URL in .env")
else:
    # Create fresh if missing
    with open(env_path, "w", encoding="utf-8") as f:
        f.write(f"DATABASE_URL={new_url}\n")
        f.write("PINECONE_HOST=https://brain-vault-k8ezddd.svc.aped-4627-b74a.pinecone.io\n")
        f.write("PINECONE_API_KEY=\n")
        f.write("OPENAI_API_KEY=\n")
        f.write("GEMINI_API_KEY=\n")
    print("Created .env with DATABASE_URL")
