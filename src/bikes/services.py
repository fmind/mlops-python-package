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
        sink (str): logging output.
        level (str): logging level.
        format (str): logging format.
        colorize (bool): colorize output.
        serialize (bool): convert to JSON.
        backtrace (bool): enable exception trace.
        diagnose (bool): enable variable display.
        catch (bool): catch errors during log handling.
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
    """Service for MLflow tracking and registry.

    Attributes:
        autolog_disable (bool): disable autologging.
        autolog_disable_for_unsupported_versions (bool): disable autologging for unsupported versions.
        autolog_exclusive (bool): If True, enables exclusive autologging.
        autolog_log_input_examples (bool): If True, logs input examples during autologging.
        autolog_log_model_signatures (bool): If True, logs model signatures during autologging.
        autolog_log_models (bool): If True, enables logging of models during autologging.
        autolog_log_datasets (bool): If True, logs datasets used during autologging.
        autolog_silent (bool): If True, suppresses all MLflow warnings during autologging.
        tracking_uri (str): The URI for the MLflow tracking server.
        experiment_name (str): The name of the experiment to log runs under.
        registry_uri (str): The URI for the MLflow model registry.
        registry_name (str): The name of the registry.
    """

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
    tracking_uri: str = "http://localhost:5000"
    experiment_name: str = "bikes"
    # registry
    registry_uri: str = "http://localhost:5000"
    registry_name: str = "bikes"

    def start(self):
        """Start the mlflow service."""
        # uri
        mlflow.set_tracking_uri(uri=self.tracking_uri)
        mlflow.set_registry_uri(uri=self.registry_uri)
        # experiment
        mlflow.set_experiment(experiment_name=self.experiment_name)
        # autologging
        mlflow.autolog(
            disable=self.autolog_disable,
            disable_for_unsupported_versions=self.autolog_disable_for_unsupported_versions,
            exclusive=self.autolog_exclusive,
            log_input_examples=self.autolog_log_input_examples,
            log_model_signatures=self.autolog_log_model_signatures,
            log_models=self.autolog_log_models,
            silent=self.autolog_silent,
        )

    def client(self) -> MlflowClient:
        """Get an instance of MLflow client."""
        return MlflowClient(tracking_uri=self.tracking_uri, registry_uri=self.registry_uri)

    def register(
        self, run_id: str, path: str, alias: str
    ) -> mlflow.entities.model_registry.ModelVersion:
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
        client.set_registered_model_alias(
            name=self.registry_name, alias=alias, version=version.version
        )
        return version
