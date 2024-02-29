"""Package tasks for pyinvoke."""

# %% IMPORTS

from invoke import task
from invoke.context import Context

from . import cleans

# %% CONFIGS

BUILD_FORMAT = "wheel"

# %% TASKS


@task(pre=[cleans.dist])
def build(ctx: Context, format: str = BUILD_FORMAT) -> None:
    """Build a python package with the given format."""
    ctx.run(f"poetry build --format={format}")


@task(pre=[build], default=True)
def all(_: Context) -> None:
    """Run all package tasks."""
