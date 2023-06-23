"""Docker tasks for pyinvoke."""
# pylint: disable=redefined-builtin

# %% IMPORTS

from invoke import task
from invoke.context import Context

from . import package

# %% TASKS


@task(pre=[package.build])
def build(ctx: Context) -> None:
    """Build the docker image."""
    ctx.run(f"docker build -t {ctx.project.name}:latest .")


@task
def run(ctx: Context) -> None:
    """Run the docker image."""
    ctx.run(f"docker run --rm {ctx.project.name}:latest")


@task(pre=[build, run], default=True)
def all(_: Context) -> None:
    """Run all docker tasks."""
