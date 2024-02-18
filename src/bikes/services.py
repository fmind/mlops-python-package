"""Manage global context during execution."""

# %% IMPORTS

import abc
import sys
import typing as T

import mlflow
import pydantic as pdt
from loguru import logger
from mlflow.tracking import MlflowClient

# %% SERVICES


class Service(abc.ABC, pdt.BaseModel, strict=True):
    """Base class for a global service.

    Use services to manage global contexts.
    e.g., logger object, mlflow client, spark context, ...
    """

    @abc.abstractmethod
    def start(self) -> None:
        """Start the service."""

    def stop(self) -> None:
        """Stop the service."""
        # does nothing by default


class LoggerService(Service):
    """Service for logging messages.

    https://loguru.readthedocs.io/en/stable/api/logger.html

    Attributes:
        sink: logging output.
        level: logging level.
        format: logging format.
        colorize: colorize output.
        serialize: convert to JSON.
        backtrace: enable exception trace.
        diagnose: enable variable display.
        catch: catch errors during log handling.
    """

    sink: str = "stderr"
    level: str = "INFO"
    format: str = (
        "<green>[{time:YYYY-MM-DD HH:mm:ss.SSS}]</green>"
        "<level>[{level}]</level>"
        "<cyan>[{name}:{function}:{line}]</cyan>"
        " <level>{message}</level>"
    )
    colorize: bool = True
    serialize: bool = False
    backtrace: bool = True
    diagnose: bool = False
    catch: bool = True

    @T.override
    def start(self) -> None:
        # sinks
        sinks = {
            "stderr": sys.stderr,
            "stdout": sys.stdout,
        }
        # cleanup
        logger.remove()
        # convert
        config = self.model_dump()
        # replace
        # - use standard sinks or keep the original
        config["sink"] = sinks.get(config["sink"], config["sink"])
        # config
        logger.add(**config)


class MLflowService(Service):
    """Service for MLflow tracking and registry."""

    # autolog
    autolog_disable: bool = False
    autolog_disable_for_unsupported_versions: bool = False
    autolog_exclusive: bool = False
    autolog_log_input_examples: bool = True
    autolog_log_model_signatures: bool = True
    autolog_log_models: bool = False
    autolog_log_datasets: bool = True
    autolog_silent: bool = False
    # tracking
    tracking_uri: str = "./models"
    experiment_name: str = "bikes"
    # registry
    registry_uri: str = "./models"
    registry_name: str = "bikes"

    def start(self):
        """Start the mlflow service."""
        mlflow.autolog(
            disable=self.autolog_disable,
            disable_for_unsupported_versions=self.autolog_disable_for_unsupported_versions,
            exclusive=self.autolog_exclusive,
            log_input_examples=self.autolog_log_input_examples,
            log_model_signatures=self.autolog_log_model_signatures,
            log_models=self.autolog_log_models,
            silent=self.autolog_silent,
        )
        mlflow.set_tracking_uri(uri=self.tracking_uri)
        mlflow.set_registry_uri(uri=self.registry_uri)
        mlflow.set_experiment(experiment_name=self.experiment_name)

    def client(self) -> MlflowClient:
        """Get an instance of MLflow client."""
        return MlflowClient(tracking_uri=self.tracking_uri, registry_uri=self.registry_uri)

    def register(self, run_id: str, path: str, alias: str) -> mlflow.entities.model_registry.ModelVersion:
        """Register a model to mlflow registry.

        Args:
            run_id (str): id of mlflow run.
            path (str): path of artifact.
            alias (str): model alias.

        Returns:
            mlflow.entities.model_registry.ModelVersion: registered version.
        """
        client = self.client()
        model_uri = f"runs:/{run_id}/{path}"
        version = mlflow.register_model(model_uri=model_uri, name=self.registry_name)
        client.set_registered_model_alias(name=self.registry_name, alias=alias, version=version.version)
        return version
