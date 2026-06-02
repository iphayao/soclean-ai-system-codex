import os

from celery import Celery


def _bool_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


broker_url = os.getenv("CELERY_BROKER_URL", os.getenv("REDIS_URL", "redis://localhost:6379/0"))
result_backend = os.getenv("CELERY_RESULT_BACKEND", broker_url)

celery_app = Celery(
    "soclean_content_system",
    broker=broker_url,
    backend=result_backend,
    include=["app.tasks.content_generation"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    task_always_eager=_bool_env("CELERY_TASK_ALWAYS_EAGER"),
    task_eager_propagates=True,
)
