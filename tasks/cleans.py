"""Clean tasks for pyinvoke."""

# %% IMPORTS

from invoke.context import Context
from invoke.tasks import task

# %% TASKS

# %% - Tools


@task
def mypy(ctx: Context) -> None:
    """Clean the mypy tool."""
    ctx.run("rm -rf .mypy_cache/")


@task
def ruff(ctx: Context) -> None:
    """Clean the ruff tool."""
    ctx.run("rm -rf .ruff_cache/")


@task
def pytest(ctx: Context) -> None:
    """Clean the pytest tool."""
    ctx.run("rm -rf .pytest_cache/")


@task
def coverage(ctx: Context) -> None:
    """Clean the coverage tool."""
    ctx.run("rm -f .coverage*")


# %% - Folders


@task
def dist(ctx: Context) -> None:
    """Clean the dist folder."""
    ctx.run("rm -f dist/*")


@task
def docs(ctx: Context) -> None:
    """Clean the docs folder."""
    ctx.run("rm -rf docs/*")


@task
def cache(ctx: Context) -> None:
    """Clean the cache folder."""
    ctx.run("rm -rf .cache/")


@task
def mlruns(ctx: Context) -> None:
    """Clean the mlruns folder."""
    ctx.run("rm -rf mlruns/*")


@task
def outputs(ctx: Context) -> None:
    """Clean the outputs folder."""
    ctx.run("rm -rf outputs/*")


# %% - Sources


@task
def venv(ctx: Context) -> None:
    """Clean the venv folder."""
    ctx.run("rm -rf .venv/")


@task
def poetry(ctx: Context) -> None:
    """Clean poetry lock file."""
    ctx.run("rm -f poetry.lock")


@task
def python(ctx: Context) -> None:
    """Clean python caches and bytecodes."""
    ctx.run("find . -type f -name '*.py[co]' -delete")
    ctx.run(r"find . -type d -name __pycache__ -exec rm -r {} \+")


# %% PROJECTS


@task
def requirements(ctx: Context) -> None:
    """Clean the project requirements file."""
    ctx.run("rm -f requirements.txt")


@task
def environment(ctx: Context) -> None:
    """Clean the project environment file."""
    ctx.run("rm -f python_env.yaml")


# %% - Combines


@task(pre=[mypy, ruff, pytest, coverage])
def tools(_: Context) -> None:
    """Run all tools tasks."""


@task(pre=[dist, docs, cache, mlruns, outputs])
def folders(_: Context) -> None:
    """Run all folders tasks."""


@task(pre=[venv, poetry, python])
def sources(_: Context) -> None:
    """Run all sources tasks."""


@task(pre=[requirements, environment])
def projects(_: Context) -> None:
    """Run all projects tasks."""


@task(pre=[tools, folders], default=True)
def all(_: Context) -> None:
    """Run all tools and folders tasks."""


@task(pre=[all, sources, projects])
def reset(_: Context) -> None:
    """Run all tools, folders, sources, and projects tasks."""
