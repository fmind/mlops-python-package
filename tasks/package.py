"""Package tasks for pyinvoke."""
# pylint: disable=redefined-builtin

# %% IMPORTS

from invoke import task
from invoke.context import Context

from . import clean

# %% TASKS


@task
def build(ctx: Context) -> None:
    """Build a wheel package."""
    ctx.run("poetry build -f wheel")


@task(pre=[clean.dist, build], default=True)
def all(_: Context) -> None:
    """Run all package tasks."""
