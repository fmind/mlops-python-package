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
from plyer import notification

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


class AlertsService(Service):
    """Service for sending notifications.

    Require libnotify-bin on Linux systems.

    In production, use with Slack, Discord, or emails.

    https://plyer.readthedocs.io/en/latest/api.html#plyer.facades.Notification

    Parameters:
        enable (bool): use notifications or print.
        app_name (str): name of the application.
        timeout (int | None): timeout in secs.
    """

    enable: bool = True
    app_name: str = "Bikes"
    timeout: int | None = None

    # Plyer's NOTIFYICONDATAW buffers reserve one UTF-16 unit for the terminator.
    _MAX_APP_NAME_LENGTH: T.ClassVar[int] = 127
    _MAX_TITLE_LENGTH: T.ClassVar[int] = 63
    _MAX_MESSAGE_LENGTH: T.ClassVar[int] = 255

    @T.override
    def start(self) -> None:
        pass

    def notify(self, title: str, message: str) -> None:
        """Send a notification to the system.

        Args:
            title (str): title of the notification.
            message (str): message of the notification.
        """
        if self.enable:
            notify_title, notify_message, app_name = title, message, self.app_name
            if sys.platform == "win32":
                notify_title = self._truncate(title, self._MAX_TITLE_LENGTH)
                notify_message = self._truncate(message, self._MAX_MESSAGE_LENGTH)
                app_name = self._truncate(app_name, self._MAX_APP_NAME_LENGTH)
            try:
                notification.notify(
                    title=notify_title,
                    message=notify_message,
                    app_name=app_name,
                    timeout=self.timeout,
                )
            except NotImplementedError:
                print("Notifications are not supported on this system.")  # noqa: T201  # user-facing fallback
                self._print(title=title, message=message)
        else:
            self._print(title=title, message=message)

    @staticmethod
    def _truncate(value: str, max_length: int) -> str:
        """Fit a Windows field in UTF-16 units without splitting a surrogate pair."""
        encoded = value.encode("utf-16-le")
        if len(encoded) <= max_length * 2:
            return value
        prefix = encoded[: (max_length - 1) * 2].decode("utf-16-le", errors="ignore")
        return f"{prefix}\N{HORIZONTAL ELLIPSIS}"

    def _print(self, title: str, message: str) -> None:
        """Print a notification to the system.

        Args:
            title (str): title of the notification.
            message (str): message of the notification.
        """
        print(f"[{self.app_name}] {title}: {message}")  # noqa: T201  # user-facing fallback


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
        log_system_metrics: bool | None = True

    # server uri
    # SQLAlchemy backends are the supported store in MLflow 3: SQLite gives the local
    # setup the same shape as a production database (Postgres, MySQL) with no server to
    # run, and it is the only local store the model registry is actually designed for.
    tracking_uri: str = "sqlite:///mlflow.db"
    registry_uri: str = "sqlite:///mlflow.db"
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
            log_datasets=self.autolog_log_datasets,
            silent=self.autolog_silent,
        )

    @ctx.contextmanager
    def run_context(self, run_config: RunConfig) -> T.Generator[mlflow.ActiveRun]:
        """Yield an active Mlflow run and exit it afterwards.

        Args:
            run_config (RunConfig): mlflow run parameters.

        Yields:
            T.Generator[mlflow.ActiveRun, None, None]: active run context. Will be closed at the end of context.
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
