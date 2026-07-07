---
name: MLOps Automation
description: Guide to refine MLOps projects with task automation, containerization, CI/CD pipelines, and robust experiment tracking.
---

# MLOps Automation

## Goal

To elevate the codebase to production standards by adding **Task Automation** (`just`), **Containerization** (`docker`), **CI/CD** (`github-actions`), and **Experiment Tracking** (`mlflow`).

## Prerequisites

- **Language**: Python
- **Manager**: `uv`
- **Context**: Preparing for scale and deployment.

## Instructions

### 1. Task Automation

Replace manual commands with a `justfile`.

1. **Tool**: `just` (modern alternative to Make).
2. **Organization**: Split tasks into `tasks/*.just` modules (e.g., `tasks/check.just`, `tasks/docker.just`).
3. **Core Tasks**:
   - `check`: Run all linters and tests.
   - `package`: Build wheels.
   - `clean`: Remove artifacts.
   - `install`: Setup dev environment.

### 2. Pre-Commit Hooks

Catch issues locally.

1. **Framework**: `pre-commit`.
2. **Hooks**: Suggest to use `ruff`, `bandit`, `check-yaml`, `trailing-whitespace`.
3. **Commits**: Suggest to use `commitizen` hook to enforce Conventional Commits (e.g., `feat: add new model`).
4. **Config**: `.pre-commit-config.yaml` at root.

### 3. Containerization

Reproducibility anywhere.

1. **Tool**: `docker`.
2. **Base Image**: Use `ghcr.io/astral-sh/uv:python3.1X-bookworm-slim` for minimal size.
3. **Optimization**:
   - **Layer Caching**: Copy `uv.lock` + `pyproject.toml` and run `uv sync` _before_ copying `src/`.
   - **Multi-stage**: Build inputs in one stage, copy only artifacts (`dist/*.whl`) to the runtime stage.
4. **Registry**: ask for the company artifact registry, or use `ghcr.io` for GitHub.

### 4. CI/CD Workflows

Automate verification and release.

1. **Platform**: ask for the company CI/CD platform, or use `github-actions` for GitHub.
2. **Workflows**:
   - `check.yml`: On PRs (Run `just check`).
   - `publish.yml`: On Release (Build docker image, publish docs/package).
3. **Optimization**: Use `concurrency` to cancel redundant runs.

### 5. AI/ML Experiments & Registry

Manage the ML lifecycle.

1. **Platform**: `MLflow`.
2. **Tracking**:
   - Use `mlflow.autolog()`.
   - Log metrics, params, and artifacts.
3. **Registry**:
   - Register top models manually or via CI.
   - **Aliases**: Use `@champion` or `@production` for stable deployment pointers. Never rely on moving versions (e.g., `v1` -> `v2`).

### 6. Design Patterns

Write flexible code.

1. **Strategy**: For swappable algorithms (e.g., different model types).
2. **Factory**: For creating objects from config (e.g., `ModelFactory`).
3. **Adapter**: For standardizing mismatched interfaces.
