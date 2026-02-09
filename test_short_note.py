import asyncio
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.services.llm_service import llm_service

async def main():
    print("--- Testing Short Note Logic ---")
    
    test_cases = [
        "",
        "Hi",
        "A",
        "12",
        "123", # 3 chars
        "1234", # 4 chars
        "   ", # 3 spaces
        "\n\n", # 2 newlines
    ]
    
    for text in test_cases:
        print(f"\nTesting Content: '{text}' (len={len(text)})")
        try:
            # existing_tags=[], api_key=None (fallback to system/env)
            # We assume system has keys configured, or we mock
            # For this logic check, keys don't matter if it hits the early return
            meta = await llm_service.extract_metadata(text)
            print(f"Result Title: {meta.get('title')}")
            print(f"Result: {meta}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
