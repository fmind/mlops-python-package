"""Package tasks for pyinvoke."""

# pylint: disable=redefined-builtin

# %% IMPORTS

from invoke import task
from invoke.context import Context

from . import cleans

# %% CONFIGS

BUILD_FORMAT = "wheel"

# %% TASKS


@task(pre=[cleans.dist])
def build(ctx: Context) -> None:
    """Build a wheel package."""
    ctx.run(f"poetry build --format={BUILD_FORMAT}")


@task(pre=[build], default=True)
def all(_: Context) -> None:
    """Run all package tasks."""
