"""Manage global context during execution."""

# %% IMPORTS

from __future__ import annotations

import abc
import contextlib as ctx
import sys
import typing as T

import loguru
import mlflow
import mlflow.tracking as mt
import pydantic as pdt

# %% SERVICES


class Service(abc.ABC, pdt.BaseModel, strict=True, frozen=True, extra="forbid"):
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

    Parameters:
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
    level: str = "DEBUG"
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
        loguru.logger.remove()
        config = self.model_dump()
        # use standard sinks or keep the original
        sinks = {"stderr": sys.stderr, "stdout": sys.stdout}
        config["sink"] = sinks.get(config["sink"], config["sink"])
        loguru.logger.add(**config)

    def logger(self) -> loguru.Logger:
        """Return the main logger.

        Returns:
            loguru.Logger: the main logger.
        """
        return loguru.logger


class MlflowService(Service):
    """Service for Mlflow tracking and registry.

    Parameters:
        tracking_uri (str): the URI for the Mlflow tracking server.
        registry_uri (str): the URI for the Mlflow model registry.
        experiment_name (str): the name of tracking experiment.
        registry_name (str): the name of model registry.
        autolog_disable (bool): disable autologging.
        autolog_disable_for_unsupported_versions (bool): disable autologging for unsupported versions.
        autolog_exclusive (bool): If True, enables exclusive autologging.
        autolog_log_input_examples (bool): If True, logs input examples during autologging.
        autolog_log_model_signatures (bool): If True, logs model signatures during autologging.
        autolog_log_models (bool): If True, enables logging of models during autologging.
        autolog_log_datasets (bool): If True, logs datasets used during autologging.
        autolog_silent (bool): If True, suppresses all Mlflow warnings during autologging.
    """

    class RunConfig(pdt.BaseModel, strict=True, frozen=True, extra="forbid"):
        """Run configuration for Mlflow tracking.

        Parameters:
            name (str): name of the run.
            description (str | None): description of the run.
            tags (dict[str, T.Any] | None): tags for the run.
            log_system_metrics (bool | None): enable system metrics logging.
        """

        name: str
        description: str | None = None
        tags: dict[str, T.Any] | None = None
        log_system_metrics: bool | None = None

    # server uri
    tracking_uri: str = "./mlruns"
    registry_uri: str = "./mlruns"
    # experiment
    experiment_name: str = "bikes"
    # registry
    registry_name: str = "bikes"
    # autolog
    autolog_disable: bool = False
    autolog_disable_for_unsupported_versions: bool = False
    autolog_exclusive: bool = False
    autolog_log_input_examples: bool = True
    autolog_log_model_signatures: bool = True
    autolog_log_models: bool = False
    autolog_log_datasets: bool = False
    autolog_silent: bool = False

    @T.override
    def start(self) -> None:
        # server uri
        mlflow.set_tracking_uri(uri=self.tracking_uri)
        mlflow.set_registry_uri(uri=self.registry_uri)
        # experiment
        mlflow.set_experiment(experiment_name=self.experiment_name)
        # autolog
        mlflow.autolog(
            disable=self.autolog_disable,
            disable_for_unsupported_versions=self.autolog_disable_for_unsupported_versions,
            exclusive=self.autolog_exclusive,
            log_input_examples=self.autolog_log_input_examples,
            log_model_signatures=self.autolog_log_model_signatures,
            log_models=self.autolog_log_models,
            silent=self.autolog_silent,
        )

    @ctx.contextmanager
    def run_context(self, run_config: RunConfig) -> T.Generator[mlflow.ActiveRun, None, None]:
        """Yield an active Mlflow run and exit it afterwards.

        Args:
            run (str): run parameters.

        Yields:
            T.Generator[mlflow.ActiveRun, None, None]: active run context. Will be closed as the end of context.
        """
        with mlflow.start_run(
            run_name=run_config.name,
            tags=run_config.tags,
            description=run_config.description,
            log_system_metrics=run_config.log_system_metrics,
        ) as run:
            yield run

    def client(self) -> mt.MlflowClient:
        """Return a new Mlflow client.

        Returns:
            MlflowClient: the mlflow client.
        """
        return mt.MlflowClient(tracking_uri=self.tracking_uri, registry_uri=self.registry_uri)
