# Changelog

All notable changes to this project are documented in this file.

## [5.0.0] - 2026-07-07

### 🚀 Features

- Add Agent Skills.
- [**breaking**] Migrate to canonical stack (mise, lefthook, ty, dprint, git-cliff, uv_build), Python 3.14, MLflow 3

### 📚 Documentation

- _(fix)_ `PyInvoke` replaced by `just` (#70)
- _(readme)_ Add Pytest Cov as an alternative for code coverage (#106)

### ⚙️ Build & CI

- _(deps)_ Bump virtualenv from 20.29.2 to 20.29.3 (#56)
- _(deps)_ Bump ipython from 9.0.0 to 9.0.2 (#59)
- _(deps)_ Bump pywin32 from 308 to 310 (#61)
- _(deps)_ Bump argcomplete from 3.5.3 to 3.6.1 (#63)
- _(deps)_ Bump ruff from 0.9.9 to 0.11.2 (#64)
- _(deps)_ Bump pandas-stubs from 2.2.3.241126 to 2.2.3.250308 (#65)
- _(deps)_ Bump identify from 2.6.8 to 2.6.9 (#66)
- _(deps)_ Bump filelock from 3.17.0 to 3.18.0 (#67)
- _(deps)_ Bump types-pytz from 2025.1.0.20250204 to 2025.2.0.20250326 (#68)
- _(deps)_ Bump rpds-py from 0.23.1 to 0.24.0 (#69)

## [4.0.0] - 2025-03-04

### 🐛 Bug Fixes

- _(workflows)_ Fix just in workflows

### ♻️ Refactor

- _(cruft)_ Update to new template version

## [2.0.0] - 2024-07-28

### 🐛 Bug Fixes

- _(dependencies)_ Add setuptools to main dependency for mlflow
- _(mlproject)_ Fix calling mlflow run by adding project run in front

### 🧹 Miscellaneous

- _(indicators)_ Compute run time for indicators
- _(typos)_ Fix typos in code and comments
- _(docs)_ Fix docstrings in tasks
- _(pre-commit)_ Add poetry-check pre commit

### 📦 Other

- Version 1.1.1 → 1.1.2
- Version 1.1.2 → 1.1.3
- Version 1.1.3 → 2.0.0

## [1.1.1] - 2024-07-23

### 🐛 Bug Fixes

- _(version)_ Bump
- _(publish)_ Fix publication workflow by installing dev dependencies

### 📚 Documentation

- _(readme)_ Added link to the MLOps Coding Course

### 🧹 Miscellaneous

- _(notebook)_ Switch prototype from light to dark mode

### 📦 Other

- Version 1.0.0 → 1.0.1
- Version 1.1.0 → 1.1.1

## [0.8.0] - 2024-03-18

### 🐛 Bug Fixes

- _(version)_ Bump version number
- _(publish)_ Fix ref name in publish workflow

## [0.1.0] - 2023-06-23
