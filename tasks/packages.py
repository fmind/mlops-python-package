"""Package tasks of the project."""

# %% IMPORTS

from invoke.context import Context
from invoke.tasks import task

from . import cleans

# %% TASKS


@task(pre=[cleans.dist])
def build(ctx: Context) -> None:
    """Build the python package."""
    ctx.run("uv build --wheel")


@task(pre=[build], default=True)
def all(_: Context) -> None:
    """Run all package tasks."""
