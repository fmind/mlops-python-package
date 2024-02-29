"""Carbons tasks for pyinvoke."""

# %% IMPORTS

from invoke import task
from invoke.context import Context

# %% TASKS


@task
def board(ctx: Context, filepath: str = "outputs/emissions.csv", port: int = 8050) -> None:
    """Visualize carbon emissions data at file path from the carbon board app."""
    ctx.run(f"poetry run carbonboard --filepath={filepath} --port={port}")


@task(pre=[board], default=True)
def all(_: Context) -> None:
    """Run all carbon tasks."""
