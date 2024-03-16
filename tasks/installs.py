"""Install tasks for pyinvoke."""

# %% IMPORTS

from invoke.context import Context
from invoke.tasks import task

# %% TASKS


@task
def poetry(ctx: Context) -> None:
    """Install poetry packages."""
    ctx.run("poetry install")


@task
def pre_commit(ctx: Context) -> None:
    """Install pre-commit hooks on git."""
    ctx.run("poetry run pre-commit install --hook-type pre-push")
    ctx.run("poetry run pre-commit install --hook-type commit-msg")


@task(pre=[poetry, pre_commit], default=True)
def all(_: Context) -> None:
    """Run all install tasks."""
