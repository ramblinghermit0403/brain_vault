import os

env_path = ".env"

if os.path.exists(env_path):
    print(f"Reading {env_path}...")
    with open(env_path, "rb") as f:
        content = f.read()
    
    # Check for BOM
    if content.startswith(b'\xef\xbb\xbf'):
        print("BOM detected! Removing it...")
        new_content = content[3:]
        with open(env_path, "wb") as f:
            f.write(new_content)
        print("BOM removed successfully.")
    else:
        print("No BOM detected.")
else:
    print(".env not found")
