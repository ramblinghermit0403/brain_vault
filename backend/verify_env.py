from app.core.config import settings, BASE_DIR
import os

print(f"BASE_DIR: {BASE_DIR}")
env_path = os.path.join(BASE_DIR, ".env")
print(f"Checking .env at: {env_path}")
if os.path.exists(env_path):
    print("File exists.")
    with open(env_path, 'r') as f:
        lines = f.readlines()
        print("Checking .env lines:")
        for line in lines:
            if "API_KEY" in line:
                print(f"Found line: {line.strip()}")
else:
    print("File does NOT exist.")

print("-" * 20)
print("Checking Settings Values:")
print(f"OPENAI_API_KEY: '{settings.OPENAI_API_KEY}'")
print(f"GOOGLE_API_KEY: '{settings.GOOGLE_API_KEY}'")
print(f"GEMINI_API_KEY: '{settings.GEMINI_API_KEY}'")
