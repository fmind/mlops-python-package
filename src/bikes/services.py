"""Manage global context during program execution."""

# %% IMPORTS

import abc
import sys
import typing as T

import pydantic as pdt
from loguru import logger

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

    # reference: https://loguru.readthedocs.io/en/stable/api/logger.html

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
