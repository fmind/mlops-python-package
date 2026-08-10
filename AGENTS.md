# AGENTS.md

Context and rules for AI agents working in this repository. Humans should start with `README.md`.

## Project overview

- **Name**: bikes — a production-shaped MLOps package that predicts the number of bikes available.
- **Description**: reference implementation for the [MLOps Coding Course](https://mlops-coding-course.fmind.dev), generated from [cookiecutter-mlops-package](https://github.com/fmind/cookiecutter-mlops-package).
- **Language**: Python 3.14+ (`pyproject.toml`), managed with `uv`.
- **Stack**: MLflow (tracking, registry, projects, evaluation), scikit-learn, pandas, Pydantic + Pandera validation, OmegaConf YAML configs, loguru.
- **Skills**: the reusable practices behind this package are published as Agent Skills in [mlops-coding-skills](https://github.com/MLOps-Courses/mlops-coding-skills). Install them from there rather than vendoring a copy here — a copy drifts, and this repository already lost a month to proving it.

## Setup & core commands

All work goes through `mise` (see `mise.toml`); git hooks (`lefthook.yml`) and CI call the same tasks.

- Everything: `mise run all` — format, check, test, build. This is the gate; CI runs this exact task and nothing else.
- Install: `mise run install` — sync the virtualenv (`uv sync`) and install git hooks.
- Format: `mise run format` — `ruff` (import sort + format, including Python inside Markdown) and `dprint` (JSON/Markdown/TOML/YAML).
- Check: `mise run check` — `ruff` lint, `ty` types, `pip-audit` deps, `dprint`/`validate-pyproject`/`uv lock` format, `gitleaks` secrets, `trivy` filesystem scan, `hadolint` Dockerfile, `actionlint` + `zizmor` workflows.
- Test: `mise run test` — `pytest` with coverage (fails under 100%); `mise run test:parallel` is a faster, coverage-free local loop.
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
- **MLflow**: tracking and registry run on a SQLite backend (`sqlite:///mlflow.db`); artifact files stay on disk under `./mlruns`. This is the same SQLAlchemy store shape as a production Postgres and the store the model registry is designed for, so moving up is a `MLFLOW_TRACKING_URI` change, not a rewrite. Models are logged with `name=` and referenced by `models:/name@alias` or `models:/name/version`.
- **Commits**: Conventional Commits (`feat:`, `fix:`, `refactor:`, `chore:`); no attribution in commit messages. Releases use `git-cliff` (see the release process).

## Repository layout

- `src/bikes/` — package: `core/` (metrics, models, schemas), `io/` (configs, datasets, registries, services), `jobs/` (tuning, training, promotion, inference, evaluations, explanations), `utils/` (searchers, signers, splitters), plus `settings.py`, `scripts.py`, `__main__.py`.
- `confs/` — one OmegaConf YAML per MLflow job; `tests/` — `pytest` suite mirroring `src/` with fixtures in `conftest.py`.
- `pyproject.toml` — dependencies and `ruff`/`ty`/`pytest` config; `mise.toml`/`mise.lock` — tasks and pinned, locked tools; `lefthook.yml` — git hooks; `dprint.jsonc`/`trivy.yaml`/`cliff.toml` — formatter, scanner, changelog config.
- `.github/` — `workflows/` (`ci.yml` runs `mise run all`, `cd.yml` publishes docs and the image, `security.yml` rescans the full history weekly), `dependabot.yml`, `zizmor.yml`, `rulesets/main.json`.
- `Dockerfile`/`docker-compose.yml`/`MLproject` — container image, local MLflow server, and MLflow Projects reproducible runs (`--env-manager=local` reuses the uv environment, so there is no `python_env.yaml`).
