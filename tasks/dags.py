"""DAG tasks for pyinvoke."""

# %% IMPORTS

from invoke.context import Context
from invoke.tasks import call, task

# %% TASKS


@task
def job(ctx: Context, name: str) -> None:
    """Run the project for the given job name."""
    ctx.run(f"poetry run {ctx.project.name} confs/{name}.yaml")


@task(
    pre=[
        call(job, name="tuning"),  # type: ignore[arg-type]
        call(job, name="training"),  # type: ignore[arg-type]
        call(job, name="promotion"),  # type: ignore[arg-type]
        call(job, name="inference"),  # type: ignore[arg-type]
    ],
    default=True,
)
def all(_: Context) -> None:
    """Run all DAG tasks."""
