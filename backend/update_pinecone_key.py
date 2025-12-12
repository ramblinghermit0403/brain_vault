import os

# Read existing .env
env_path = ".env"
if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
else:
    lines = []

new_key = "pcsk_3uPA8C_SAcmv2fpyunPdKgZjJ1CR5Hn4K9gG7ns9si5dVcgCEALRnURaVyG7GRYP3ZYMU6"
key_found = False
new_lines = []

for line in lines:
    if line.startswith("PINECONE_API_KEY="):
        new_lines.append(f"PINECONE_API_KEY={new_key}\n")
        key_found = True
    else:
        new_lines.append(line)

if not key_found:
    new_lines.append(f"PINECONE_API_KEY={new_key}\n")

with open(env_path, "w", encoding="utf-8") as f:
    f.writelines(new_lines)
    
print("Updated PINECONE_API_KEY in .env")
