from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "brain_vault_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.REDIS_URL, # Use separate Redis URL if configured, or default to broker
    include=["app.worker"]
)
print(f"Celery App Initialized with broker: {settings.CELERY_BROKER_URL}")

celery_app.conf.task_routes = {
    "app.worker.process_memory_metadata_task": "celery",
    "app.worker.ingest_memory_task": "celery",
    "app.worker.dedupe_memory_task": "celery",
    "app.worker.extract_chat_facts_task": "celery",
}

# Optional: Retry customization
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
