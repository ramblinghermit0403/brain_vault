import asyncio
import json
from redis import asyncio as aioredis

async def main():
    print("Connecting to Redis...")
    # Matches CELERY_BROKER_URL
    redis = aioredis.from_url("redis://localhost:6379/0") 
    
    message = {
        "type": "message",
        "target_type": "broadcast",
        "payload": {
            "type": "inbox_update", 
            "id": "test_msg", 
            "action": "debug_test"
        }
    }
    
    print(f"Publishing to 'brain_vault_updates': {message}")
    await redis.publish("brain_vault_updates", json.dumps(message))
    await redis.close()
    print("Published.")

if __name__ == "__main__":
    if asyncio.get_event_loop_policy().__class__.__name__ == 'WindowsProactorEventLoopPolicy':
        # Redis-py asyncio on Windows sometimes needs SelectorEventLoop? 
        # But Uvicorn uses Proactor. Let's try default.
        pass
    asyncio.run(main())
