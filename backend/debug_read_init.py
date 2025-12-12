
import os

paths = [
    r"c:\Users\himan\OneDrive\Documents\brain_vault\backend\venv\Lib\site-packages\pinecone\__init__.py",
    r"venv\Lib\site-packages\pinecone\__init__.py"
]

for p in paths:
    if os.path.exists(p):
        print(f"Reading {p}")
        try:
            with open(p, "r", encoding="utf-8") as f:
                print(f.read())
            break
        except Exception as e:
            print(f"Error reading {p}: {e}")
    else:
        print(f"Path not found: {p}")
