"""Clean tasks for pyinvoke."""

# pylint: disable=redefined-builtin

# %% IMPORTS

from invoke import task
from invoke.context import Context

# %% TASKS


@task
def coverage(ctx: Context) -> None:
    """Clean coverage files."""
    ctx.run("rm -f .coverage*")


@task
def dist(ctx: Context) -> None:
    """Clean the dist folder."""
    ctx.run("rm -f dist/*")


@task
def docs(ctx: Context) -> None:
    """Clean the docs folder."""
    ctx.run("rm -rf docs/*")


@task
def install(ctx: Context) -> None:
    """Clean the install."""
    ctx.run("rm -rf .venv/")
    ctx.run("rm -f poetry.lock")


@task
def mypy(ctx: Context) -> None:
    """Clean the mypy folder."""
    ctx.run("rm -rf .mypy_cache/")


@task
def outputs(ctx: Context) -> None:
    """Clean the outputs folder."""
    ctx.run("rm -rf outputs/*")


@task
def pytest(ctx: Context) -> None:
    """Clean the pytest folder."""
    ctx.run("rm -rf .pytest_cache/")


@task
def python(ctx: Context) -> None:
    """Clean python files and folders."""
    ctx.run("find . -type f -name '*.py[co]' -delete")
    ctx.run("find . -type d -name __pycache__ -delete")


@task(pre=[coverage, dist, docs, mypy, pytest, python], default=True)
def all(_: Context) -> None:
    """Run all clean tasks."""


@task(pre=[all, outputs, install])
def reset(_: Context) -> None:
    """Reset the project state."""
