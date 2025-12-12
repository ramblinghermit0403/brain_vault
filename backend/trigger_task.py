from app.worker import dedupe_memory_task
try:
    print("Sending task...")
    result = dedupe_memory_task.delay(99999)
    print(f"Task sent. ID: {result.id}")
except Exception as e:
    print(f"Error sending task: {e}")
