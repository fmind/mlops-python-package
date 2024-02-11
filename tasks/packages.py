"""Package tasks for pyinvoke."""

# pylint: disable=redefined-builtin

# %% IMPORTS

from invoke import task
from invoke.context import Context

from . import cleans

# %% TASKS


@task(pre=[cleans.dist])
def build(ctx: Context) -> None:
    """Build a wheel package."""
    ctx.run("poetry build -f wheel")


@task(pre=[build], default=True)
def all(_: Context) -> None:
    """Run all package tasks."""
