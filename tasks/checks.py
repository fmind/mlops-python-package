"""Check tasks for pyinvoke."""

# %% IMPORTS

from invoke.context import Context
from invoke.tasks import task

# %% TASKS


@task
def poetry(ctx: Context) -> None:
    """Check poetry config files."""
    ctx.run("poetry check --lock")


@task
def format(ctx: Context) -> None:
    """Check the formats with ruff."""
    ctx.run("poetry run ruff format --check src/ tasks/ tests/")


@task
def type(ctx: Context) -> None:
    """Check the types with mypy."""
    ctx.run("poetry run mypy src/ tasks/ tests/")


@task
def code(ctx: Context) -> None:
    """Check the codes with ruff."""
    ctx.run("poetry run ruff check src/ tasks/ tests/")


@task
def test(ctx: Context) -> None:
    """Check the tests with pytest."""
    ctx.run("poetry run pytest --numprocesses='auto' tests/")


@task
def security(ctx: Context) -> None:
    """Check the security with bandit."""
    ctx.run("poetry run bandit --recursive --configfile=pyproject.toml src/")


@task
def coverage(ctx: Context) -> None:
    """Check the coverage with coverage."""
    ctx.run("poetry run pytest --numprocesses='auto' --cov=src/ --cov-fail-under=80 tests/")


@task(pre=[poetry, format, type, code, security, coverage], default=True)
def all(_: Context) -> None:
    """Run all check tasks."""
