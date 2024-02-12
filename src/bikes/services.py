"""Manage global contexts during execution."""

# %% IMPORTS

import abc
import sys

import pydantic as pdt
from loguru import logger

# %% SERVICES


class Service(abc.ABC, pdt.BaseModel, strict=True):
    """Base class for a global service."""

    # Note: use services to manage global contexts
    # e.g., logger object, mlflow client, spark context, ...

    @abc.abstractmethod
    def start(self) -> None:
        """Start the service."""

    def stop(self) -> None:
        """Stop the service."""
        # do nothing by default


class LoggerService(Service):
    """Service for logging messages."""

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

    def start(self) -> None:
        """Start the logger service."""
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
