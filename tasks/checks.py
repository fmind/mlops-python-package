"""Check tasks for pyinvoke."""

# pylint: disable=redefined-builtin

# %% IMPORTS

from invoke import task
from invoke.context import Context

# %% CONFIGS

COVERAGE_FAIL_UNDER = 80
PYTEST_N_PROCESSES = "auto"

# %% TASKS


@task
def code(ctx: Context) -> None:
    """Check the codes with pylint."""
    ctx.run("poetry run pylint src/ tasks/ tests/")


@task
def coverage(ctx: Context) -> None:
    """Check the coverage with coverage."""
    ctx.run(
        f"poetry run pytest --numprocesses={PYTEST_N_PROCESSES}"
        f" --cov=src/ --cov-fail-under={COVERAGE_FAIL_UNDER} tests/"
    )


@task
def format(ctx: Context) -> None:
    """Check the formats with isort and black."""
    ctx.run("poetry run isort --check src/ tasks/ tests/")
    ctx.run("poetry run black --check src/ tasks/ tests/")


@task
def poetry(ctx: Context) -> None:
    """Check poetry config files."""
    ctx.run("poetry check")


@task
def test(ctx: Context) -> None:
    """Check the tests with pytest."""
    ctx.run("poetry run pytest --numprocesses={PYTEST_N_PROCESSES} tests/")


@task
def type(ctx: Context) -> None:
    """Check the types with mypy."""
    ctx.run("poetry run mypy src/ tasks/ tests/")


@task(pre=[type, code, coverage, format, poetry], default=True)
def all(_: Context) -> None:
    """Run all check tasks."""
