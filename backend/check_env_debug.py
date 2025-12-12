import os
from app.core.config import settings
from dotenv import load_dotenv

print(f"--- Debug Env ---")
print(f"CWD: {os.getcwd()}")
print(f"Env file exists: {os.path.exists('.env')}")
if os.path.exists('.env'):
    try:
        content = open('.env', encoding='utf-8').read()
        print(f"Env content head: {content[:100]}")
    except Exception as e:
        print(f"Read error: {e}")

print(f"Settings.DATABASE_URL: {settings.DATABASE_URL}")

# Try manual load
print("Loading manual dotenv...")
load_dotenv()
print(f"OS Env DATABASE_URL: {os.environ.get('DATABASE_URL')}")
