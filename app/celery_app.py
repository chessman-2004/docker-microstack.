import os
from celery import Celery

REDIS_HOST = os.getenv("REDIS_HOST", "cache")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")

# Celery uses Redis as the message broker
celery_app = Celery(
    "worker",
    broker=f"redis://{REDIS_HOST}:{REDIS_PORT}/0",
    backend=f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)