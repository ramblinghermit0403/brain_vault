import os
import sys
from sqlalchemy import create_engine, text

sys.path.append(os.getcwd())

env_path = ".env"
found_url = None

if os.path.exists(env_path):
    print(f"Reading {env_path}...")
    with open(env_path, "r") as f:
        for line in f:
            if line.startswith("DATABASE_URL="):
                found_url = line.split("=", 1)[1].strip().strip("'").strip('"')
                break

if not found_url:
    print("DATABASE_URL not found.")
    sys.exit(0)

print("Found DATABASE_URL.")
# Simple sync URL adjustment
sync_url = found_url.replace("+asyncpg", "")
try:
    engine = create_engine(sync_url)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("Connection Successful! (Returned 1)")
except Exception as e:
    print(f"Connection Failed: {e}")
