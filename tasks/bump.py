"""Bump tasks for pyinvoke."""
# pylint: disable=redefined-builtin

# %% IMPORTS

from invoke import task
from invoke.context import Context

# %% TASKS


@task(default=True)
def release(ctx: Context, part: str) -> None:
    """Bump a release: major, minor, patch."""
    ctx.run(f"poetry run bump2version --allow-dirty {part}")


@task
def version(ctx: Context, new_version: str) -> None:
    """Bump to the new version."""
    ctx.run(f"poetry run bump2version --allow-dirty patch --new-version {new_version}")
