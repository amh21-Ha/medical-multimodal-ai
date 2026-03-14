from types import SimpleNamespace

try:
    from celery import Celery  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    class Celery:  # type: ignore[override]
        def __init__(self, *args, **kwargs):
            self.conf = SimpleNamespace(task_routes={})

        def task(self, name: str):
            def decorator(func):
                def delay(*args, **kwargs):
                    return func(*args, **kwargs)

                func.delay = delay
                return func

            return decorator

from utils.config import get_settings

settings = get_settings()

celery_app = Celery(
    "multimodal_worker",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.task_routes = {
    "workers.tasks.run_analysis": {"queue": "analysis"},
}
