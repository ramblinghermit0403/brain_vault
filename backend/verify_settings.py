import sys
import os

# Add backend to path so we can import app
sys.path.append(os.getcwd())

from app.core.config import settings

print(f"GOOGLE_API_KEY: {'Set' if settings.GOOGLE_API_KEY else 'Unset'}")
print(f"GEMINI_API_KEY: {'Set' if settings.GEMINI_API_KEY else 'Unset'}")
print(f"OPENAI_API_KEY: {'Set' if settings.OPENAI_API_KEY else 'Unset'}")
print(f"PINECONE_API_KEY: {'Set' if settings.PINECONE_API_KEY else 'Unset'}")
print(f"Loading from: {settings.Config.env_file}")

import os
env_path = os.path.join(os.getcwd(), ".env")
print(f"Checking .env at {env_path}")
if os.path.exists(env_path):
    with open(env_path, "r") as f:
        for line in f:
            if "GEMINI" in line:
                parts = line.split("=")
                key = parts[0].strip()
                val = parts[1].strip() if len(parts) > 1 else ""
                print(f"Found {key}: Len={len(val)}")
else:
    print(".env not found")


