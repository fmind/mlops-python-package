"""Manage global context during execution."""

# %% IMPORTS

import abc
import os
import sys
import typing as T

import codecarbon as cc
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


class CarbonService(Service):
    """Service for tracking carbon emissions.

    https://mlco2.github.io/codecarbon/parameters.html

    Attributes:
        log_level (str): Level of logging to output.
        project_name (str): Name of the project to track.
        measure_power_secs (int): Interval for measuring in secs.
        output_dir (str): Directory where the output files are stored.
        output_file (str): Name of the output CSV file for emissions data.
        on_csv_write (str): Specifies the action on writing to CSV (append or overwrite).
        country_iso_code (str): ISO code of the country for tracking carbon emissions offline.
    """

    # public
    # - inputs
    log_level: str = "ERROR"
    project_name: str = "bikes"
    tracking_mode: str = "machine"
    measure_power_secs: int = 5
    # - outputs
    output_dir: str = "outputs"
    output_file: str = "emissions.csv"
    on_csv_write: str = "append"
    # - offline
    country_iso_code: str = "LUX"
    # private
    _tracker: cc.OfflineEmissionsTracker | None = None

    @T.override
    def start(self) -> None:
        """Start the carbon service."""
        params = self.model_dump()
        os.makedirs(self.output_dir, exist_ok=True)
        self._tracker = cc.OfflineEmissionsTracker(**params)
        self._tracker.start()

    def stop(self) -> None:
        """Stop the carbon service."""
        assert self._tracker, "Carbon tracker should be started!"
        self._tracker.flush()
        self._tracker.stop()


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
        enable_system_metrics (bool): enable system metrics logging.
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
    # system
    enable_system_metrics: bool = True
    # tracking
    # tracking_uri: str = "http://localhost:5000"
    tracking_uri: str = "./mlruns"
    experiment_name: str = "bikes"
    # registry
    # registry_uri: str = "http://localhost:5000"
    registry_uri: str = "./mlruns"
    registry_name: str = "bikes"

    @T.override
    def start(self) -> None:
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
        # system metrics
        if self.enable_system_metrics:
            mlflow.enable_system_metrics_logging()

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
