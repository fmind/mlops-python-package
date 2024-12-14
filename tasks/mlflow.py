"""Mlflow tasks of the project."""

# %% IMPORTS

from invoke.context import Context
from invoke.tasks import task

# %% TASKS


@task
def doctor(ctx: Context) -> None:
    """Run mlflow doctor."""
    ctx.run("uv run mlflow doctor")


@task
def serve(
    ctx: Context,
    host: str = "127.0.0.1",
    port: str = "5000",
    backend_store_uri: str = "./mlruns",
) -> None:
    """Start an mlflow server."""
    ctx.run(
        f"uv run mlflow server --host={host} --port={port} --backend-store-uri={backend_store_uri}"
    )


@task(pre=[doctor, serve], default=True)
def all(_: Context) -> None:
    """Run all mlflow tasks."""
