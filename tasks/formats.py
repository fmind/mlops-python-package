"""Format tasks for pyinvoke."""

# %% IMPORTS

from invoke import task
from invoke.context import Context

# %% TASKS


@task
def code(ctx: Context) -> None:
    """Format code with ruff."""
    ctx.run("poetry run ruff format src/ tasks/ tests/")


@task(pre=[code], default=True)
def all(_: Context) -> None:
    """Run all format tasks."""
