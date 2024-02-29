"""Commits tasks for pyinvoke."""

# %% IMPORTS

from invoke import task
from invoke.context import Context

# %% TASKS


@task
def info(ctx: Context) -> None:
    """Print a guide for messages."""
    ctx.run("poetry run cz info")


@task
def bump(ctx: Context) -> None:
    """Bump the version of the package."""
    ctx.run("poetry run cz bump")


@task
def commit(ctx: Context) -> None:
    """Commit all changes with a message."""
    ctx.run("poetry run cz commit")


@task(pre=[commit], default=True)
def all(_: Context) -> None:
    """Run all commit tasks."""
