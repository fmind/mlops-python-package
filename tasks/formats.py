"""Format tasks for pyinvoke."""

# %% IMPORTS

from invoke.context import Context
from invoke.tasks import task

# %% TASKS


@task
def code(ctx: Context) -> None:
    """Format python code with ruff."""
    ctx.run("poetry run ruff format src/ tasks/ tests/")


@task(pre=[code], default=True)
def all(_: Context) -> None:
    """Run all format tasks."""
