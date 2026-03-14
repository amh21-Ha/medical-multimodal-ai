import mlflow
from mlflow.tracking import MlflowClient

from utils.config import get_settings


def register_model(model_uri: str, model_name: str) -> str:
    settings = get_settings()
    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)

    model_version = mlflow.register_model(model_uri=model_uri, name=model_name)
    return model_version.version


def transition_model_stage(model_name: str, version: str, stage: str) -> None:
    settings = get_settings()
    client = MlflowClient(tracking_uri=settings.mlflow_tracking_uri)
    client.transition_model_version_stage(name=model_name, version=version, stage=stage)
