"""Project tasks of the project."""

# mypy: disable-error-code="arg-type"

# %% IMPORTS

import json

from invoke.context import Context
from invoke.tasks import call, task

# %% CONFIGS

PYTHON_VERSION = ".python-version"
REQUIREMENTS = "requirements.txt"
ENVIRONMENT = "python_env.yaml"

# %% TASKS


@task
def requirements(ctx: Context) -> None:
    """Export the project requirements file."""
    ctx.run(
        "uv export --format=requirements-txt --no-dev "
        "--no-hashes --no-editable --no-emit-project "
        f"--output-file={REQUIREMENTS}"
    )


@task(pre=[requirements])
def environment(ctx: Context) -> None:
    """Export the project environment file."""
    with open(PYTHON_VERSION, "r") as reader:
        python = reader.read().strip()  # version
    configuration: dict[str, object] = {"python": python}
    with open(REQUIREMENTS, "r") as reader:
        dependencies: list[str] = []
        for line in reader.readlines():
            dependency = line.split(" ")[0].strip()
            if "pywin32" in dependency or "#" in dependency:
                continue
            dependencies.append(dependency)
    configuration["dependencies"] = dependencies
    with open(ENVIRONMENT, "w") as writer:
        # Safe as YAML is a superset of JSON
        json.dump(configuration, writer, indent=4)
        writer.write("\n")  # add new line at the end


@task
def run(ctx: Context, job: str) -> None:
    """Run an mlflow project from the MLproject file."""
    ctx.run(
        f"uv run mlflow run --experiment-name={ctx.project.repository}"
        f" --run-name={job.capitalize()} -P conf_file=confs/{job}.yaml ."
    )


@task(
    pre=[
        environment,
        call(run, job="tuning"),
        call(run, job="training"),
        call(run, job="promotion"),
        call(run, job="inference"),
        call(run, job="evaluations"),
        call(run, job="explanations"),
    ],
    default=True,
)
def all(_: Context) -> None:
    """Run all project tasks."""
