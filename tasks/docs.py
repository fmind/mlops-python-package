"""Docs tasks for pyinvoke."""

# pylint: disable=redefined-builtin

# %% IMPORTS

from invoke import task
from invoke.context import Context

from . import cleans

# %% TASKS


@task
def api(ctx: Context) -> None:
    """Document the API with pdoc."""
    ctx.run(f"poetry run pdoc -d google -o docs/api src/{ctx.project.name}")


@task
def serve(ctx: Context) -> None:
    """Document the API with pdoc."""
    ctx.run(f"poetry run pdoc -d google src/{ctx.project.name}")


@task(pre=[cleans.docs, api], default=True)
def all(_: Context) -> None:
    """Run all docs tasks."""
