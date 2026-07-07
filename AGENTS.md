# AGENTS.md

Context and rules for AI agents working in this repository. Humans should start with `README.md`.

## Project overview

- **Name**: bikes — a production-shaped MLOps package that predicts the number of bikes available.
- **Description**: reference implementation for the [MLOps Coding Course](https://mlops-coding-course.fmind.dev), generated from [cookiecutter-mlops-package](https://github.com/fmind/cookiecutter-mlops-package).
- **Language**: Python 3.14+ (`pyproject.toml`), managed with `uv`.
- **Stack**: MLflow (tracking, registry, projects, evaluation), scikit-learn, pandas, Pydantic + Pandera validation, OmegaConf YAML configs, loguru.

## Setup & core commands

All work goes through `mise` (see `mise.toml`); git hooks (`lefthook.yml`) and CI call the same tasks.

- Install: `mise run install` — sync the virtualenv (`uv sync`) and install git hooks.
- Format: `mise run format` — `ruff` (import sort + format) and `dprint` (JSON/Markdown/TOML/YAML).
- Check: `mise run check` — `ruff` lint, `ty` types, `pip-audit` deps, `dprint`/`validate-pyproject`/`uv lock` format, `gitleaks` secrets, `trivy` config.
- Test: `mise run test` — `pytest` with coverage (fails under 80%).
- Build: `mise run build` — `uv build` (wheel + sdist); `mise run build:image` builds the Docker image.
- Docs: `mise run docs` — `pdoc` API reference into `docs/`.
- MLflow jobs: `mise run project` runs every job; `mise run project:run <name>` runs one (`confs/<name>.yaml`).

## Definition of done

A change is complete only when, locally, `mise run format` is clean, `mise run check` reports no findings, and `mise run test` is green with new/changed behavior covered by a test. Fix root causes — never weaken an assertion, add a skip/`xfail`, loosen a type, or suppress a lint error to force a green result.

## Conventions & idioms

- **Errors with context**: raise specific exceptions and chain with `raise ... from err`; never use a bare `except` or silently swallow errors.
- **Config over hardcoding**: jobs and objects are Pydantic models parsed from OmegaConf YAML in `confs/`; validate and fail fast. Dataframes are validated at boundaries with Pandera schemas (`core/schemas.py`).
- **Typing**: modern annotations (`list[str]`, `X | Y`); keep `ty check` clean. `import typing as T` is the project convention.
- **Logging**: `loguru` via `LoggerService`; no bare prints in library code.
- **MLflow**: the file store (`./mlruns`) is opted in via `MLFLOW_ALLOW_FILE_STORE` for local development; prefer a database backend in production. Models are logged with `name=` and referenced by `models:/name@alias` or `models:/name/version`.
- **Commits**: Conventional Commits (`feat:`, `fix:`, `refactor:`, `chore:`); no attribution in commit messages. Releases use `git-cliff` (see the release process).

## Repository layout

- `src/bikes/` — package: `core/` (metrics, models, schemas), `io/` (configs, datasets, registries, services), `jobs/` (tuning, training, promotion, inference, evaluations, explanations), `utils/` (searchers, signers, splitters), plus `settings.py`, `scripts.py`, `__main__.py`.
- `confs/` — one OmegaConf YAML per MLflow job; `tests/` — `pytest` suite mirroring `src/` with fixtures in `conftest.py`.
- `pyproject.toml` — dependencies and `ruff`/`ty`/`pytest` config; `mise.toml` — tasks and pinned tools; `lefthook.yml` — git hooks; `dprint.jsonc`/`trivy.yaml`/`cliff.toml` — formatter, scanner, changelog config.
- `Dockerfile`/`docker-compose.yml`/`MLproject`/`python_env.yaml` — container image, local MLflow server, and MLflow Projects reproducible runs.
