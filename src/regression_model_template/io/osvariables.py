from typing import Any

from pydantic_settings import BaseSettings


class Singleton(object):
    # Type annotation for the _instances attribute
    _instances: dict[type, "Singleton"] = {}

    def __new__(cls: type["Singleton"], *args: tuple[Any, ...], **kwargs: dict[str, Any]) -> "Singleton":
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__new__(cls, *args, **kwargs)
        return cls._instances[cls]


class Env(Singleton, BaseSettings):
    mlflow_tracking_uri: str = "./mlruns"
    mlflow_registry_uri: str = "./mlruns"
    mlflow_experiment_name: str = "regression_model_template"
    mlflow_registered_model_name: str = "regression_model_template"

    class Config:
        case_sensitive: bool = False  # Optional: make env var lookup case-insensitive
        env_file: str = ".env"  # Enable reading from .env file
        env_file_encoding: str = "utf-8"
