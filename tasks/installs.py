"""Install tasks for pyinvoke."""

# pylint: disable=redefined-builtin

# %% IMPORTS

from invoke import task
from invoke.context import Context

# %% TASKS


@task
def poetry(ctx: Context) -> None:
    """Run poetry install."""
    ctx.run("poetry install")


@task
def pre_commit(ctx: Context) -> None:
    """Run pre-commit install."""
    ctx.run("poetry run pre-commit install")


@task(pre=[poetry, pre_commit], default=True)
def all(_: Context) -> None:
    """Run all install tasks."""
