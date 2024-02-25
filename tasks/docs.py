"""Docs tasks for pyinvoke."""

# %% IMPORTS

from invoke import task
from invoke.context import Context

from . import cleans

# %% CONFIGS

DOC_FORMAT = "google"
OUTPUT_DIR = "docs/"

# %% TASKS


@task
def api(ctx: Context) -> None:
    """Document the API with pdoc."""
    ctx.run(
        f"poetry run pdoc --docformat={DOC_FORMAT} --output-directory={OUTPUT_DIR} src/{ctx.project.name}"
    )


@task
def serve(ctx: Context) -> None:
    """Document the API with pdoc."""
    ctx.run(f"poetry run pdoc --docformat={DOC_FORMAT} src/{ctx.project.name}")


@task(pre=[cleans.docs, api], default=True)
def all(_: Context) -> None:
    """Run all docs tasks."""
