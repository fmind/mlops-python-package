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
def api(ctx: Context, format: str = DOC_FORMAT, output_dir: str = OUTPUT_DIR) -> None:
    """Document the API with pdoc using the given format and output directory."""
    ctx.run(
        f"poetry run pdoc --docformat={format} --output-directory={output_dir} src/{ctx.project.name}"
    )


@task
def serve(ctx: Context, format: str = DOC_FORMAT) -> None:
    """Serve the docs with pdoc using the given format."""
    ctx.run(f"poetry run pdoc --docformat={format} src/{ctx.project.name}")


@task(pre=[cleans.docs, api], default=True)
def all(_: Context) -> None:
    """Run all docs tasks."""
