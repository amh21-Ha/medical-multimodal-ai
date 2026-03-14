from __future__ import annotations

import logging
from typing import Any

import mlflow

from utils.config import get_settings


LOGGER = logging.getLogger(__name__)


def log_experiment_run(run_name: str, params: dict[str, Any], metrics: dict[str, float]) -> str:
    settings = get_settings()
    try:
        mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
        with mlflow.start_run(run_name=run_name) as run:
            mlflow.set_tags({
                "service": settings.app_name,
                "environment": settings.app_env,
            })
            mlflow.log_params(params)
            mlflow.log_metrics(metrics)
            return run.info.run_id
    except Exception as exc:  # pragma: no cover
        LOGGER.warning("MLflow logging failed: %s", exc)
        return "mlflow-unavailable"
