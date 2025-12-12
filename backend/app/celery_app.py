import os
from celery import Celery

# Get Redis URL from env, default to validation value or loopback
BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "brain_vault_worker",
    broker=BROKER_URL,
    backend=BROKER_URL,
    include=["app.worker"]
)
print("Celery App Initialized with include=['app.worker']")

celery_app.conf.task_routes = {
    "app.worker.process_memory_metadata_task": "celery",
    "app.worker.ingest_memory_task": "celery",
    "app.worker.dedupe_memory_task": "celery",
}

# Optional: Retry customization
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
