"""DAG tasks for pyinvoke."""

# %% IMPORTS

from invoke import call, task
from invoke.context import Context

# %% TASKS


@task
def job(ctx: Context, name: str) -> None:
    """Run the project for the given job name."""
    ctx.run(f"poetry run {ctx.project.name} confs/{name}.yaml")


@task(
    pre=[
        call(job, name="tuning"),  # type: ignore
        call(job, name="training"),  # type: ignore
        call(job, name="inference"),  # type: ignore
    ],
    default=True,
)
def all(_: Context) -> None:
    """Run all DAG tasks."""
