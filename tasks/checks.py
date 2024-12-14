"""Check tasks of the project."""

# %% IMPORTS

from invoke.context import Context
from invoke.tasks import task

# %% TASKS


@task
def format(ctx: Context) -> None:
    """Check the formats with ruff."""
    ctx.run("uv run ruff format --check src/ tasks/ tests/")


@task
def type(ctx: Context) -> None:
    """Check the types with mypy."""
    ctx.run("uv run mypy src/ tasks/ tests/")


@task
def code(ctx: Context) -> None:
    """Check the codes with ruff."""
    ctx.run("uv run ruff check src/ tasks/ tests/")


@task
def test(ctx: Context) -> None:
    """Check the tests with pytest."""
    ctx.run("uv run pytest --numprocesses=auto tests/")


@task
def security(ctx: Context) -> None:
    """Check the security with bandit."""
    ctx.run("uv run bandit --recursive --configfile=pyproject.toml src/")


@task
def coverage(ctx: Context) -> None:
    """Check the coverage with coverage."""
    ctx.run("uv run pytest --numprocesses=auto --cov=src/ --cov-fail-under=80 tests/")


@task(pre=[format, type, code, security, coverage], default=True)
def all(_: Context) -> None:
    """Run all check tasks."""
