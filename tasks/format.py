"""Format tasks for pyinvoke."""
# pylint: disable=redefined-builtin

# %% IMPORTS

from invoke import task
from invoke.context import Context

# %% TASKS


@task
def imports(ctx: Context) -> None:
    """Format code imports with isort."""
    ctx.run("poetry run isort src/ tasks/ tests/")


@task
def sources(ctx: Context) -> None:
    """Format code sources with black."""
    ctx.run("poetry run black src/ tasks/ tests/")


@task(pre=[imports, sources], default=True)
def all(_: Context) -> None:
    """Run all format tasks."""
