"""Docker tasks for pyinvoke."""

# pylint: disable=redefined-builtin

# %% IMPORTS

from invoke import task
from invoke.context import Context

from . import packages

# %% TASKS


@task
def compose(ctx: Context) -> None:
    """Start docker compose."""
    ctx.run("docker compose up")


@task(pre=[packages.build])
def build(ctx: Context) -> None:
    """Build the container image."""
    ctx.run(f"docker build -t {ctx.project.name}:latest .")


@task
def run(ctx: Context) -> None:
    """Run the container image."""
    ctx.run(f"docker run --rm {ctx.project.name}:latest")


@task(pre=[build], default=True)
def all(_: Context) -> None:
    """Run all container tasks."""
