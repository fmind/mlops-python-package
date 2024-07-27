"""Mlflow tasks for pyinvoke."""

# %% IMPORTS

from invoke.context import Context
from invoke.tasks import task

# %% TASKS


@task
def doctor(ctx: Context) -> None:
    """Run mlflow doctor."""
    ctx.run("poetry run mlflow doctor")


@task
def serve(
    ctx: Context, host: str = "127.0.0.1", port: str = "5000", backend_uri: str = "./mlruns"
) -> None:
    """Start the mlflow server."""
    ctx.run(
        f"poetry run mlflow server --host={host} --port={port} --backend-store-uri={backend_uri}"
    )


@task(pre=[doctor, serve], default=True)
def all(_: Context) -> None:
    """Run all mlflow tasks."""
