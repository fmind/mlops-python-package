"""Container tasks for pyinvoke."""

# %% IMPORTS

from invoke.context import Context
from invoke.tasks import task

from . import packages

# %% CONFIGS

IMAGE_TAG = "latest"

# %% TASKS


@task
def compose(ctx: Context) -> None:
    """Start up docker compose."""
    ctx.run("docker compose up")


@task(pre=[packages.build])
def build(ctx: Context, tag: str = IMAGE_TAG) -> None:
    """Build the container image."""
    ctx.run(f"docker build --tag={ctx.project.repository}:{tag} .")


@task
def run(ctx: Context, tag: str = IMAGE_TAG) -> None:
    """Run the container image."""
    ctx.run(f"docker run --rm {ctx.project.repository}:{tag}")


@task(pre=[build, run], default=True)
def all(_: Context) -> None:
    """Run all container tasks."""
