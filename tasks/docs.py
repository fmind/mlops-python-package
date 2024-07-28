"""Docs tasks for pyinvoke."""

# %% IMPORTS

from invoke.context import Context
from invoke.tasks import task

from . import cleans

# %% CONFIGS

DOC_FORMAT = "google"
OUTPUT_DIR = "docs/"

# %% TASKS


@task
def serve(ctx: Context, format: str = DOC_FORMAT, port: int = 8088) -> None:
    """Serve the API docs with pdoc."""
    ctx.run(f"poetry run pdoc --docformat={format} --port={port} src/{ctx.project.package}")


@task
def api(ctx: Context, format: str = DOC_FORMAT, output_dir: str = OUTPUT_DIR) -> None:
    """Generate the API docs with pdoc."""
    ctx.run(
        f"poetry run pdoc --docformat={format} --output-directory={output_dir} src/{ctx.project.package}"
    )


@task(pre=[cleans.docs, api], default=True)
def all(_: Context) -> None:
    """Run all docs tasks."""
