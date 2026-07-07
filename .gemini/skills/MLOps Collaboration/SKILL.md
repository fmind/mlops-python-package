---
name: MLOps Collaboration
description: Guide to prepare MLOps projects for sharing, collaboration, and community engagement.
---

# MLOps Collaboration

## Goal

To transform a private project into a public, collaborative resource by establishing **Governance** (License, Code of Conduct), **Documentation** (README, Contributing), **Standardization** (Templates, Workstations), and **Release Management**.

## Prerequisites

- **Language**: Python
- **Platform**: GitHub
- **Context**: Open sourcing or team collaboration.

## Instructions

### 1. Repository Governance

Set the rules of engagement.

1. **Code of Conduct**: Add `CODE_OF_CONDUCT.md` to foster a safe community.
2. **Protection**: Protect the `main` branch (require PRs, status checks).
3. **Review**: Automate preliminary reviews with tools like **Gemini Code Assist** (`.gemini/config.yaml`).
4. **Ignore**: Comprehensive `.gitignore` (exclude secrets, data, venvs).

### 2. Comprehensive Documentation

Make the project usable and understandable.

1. **README.md**: The landing page (Badges, Hook, Quickstart).
2. **MkDocs**: Use for full documentation sites (API ref, tutorials) when `README.md` gets too long.
3. **CONTRIBUTING.md**: Guide for developers (env setup, PR process, testing standards).
4. **CHANGELOG.md**: Track version history (use **Keep a Changelog** format).

### 3. Standardization & Workstations

Eliminate "it works on my machine".

1. **Templates**: Use `cookiecutter` for scaffolding and `cruft update` to keep projects synced.
2. **Workstations**: Add `.devcontainer/devcontainer.json`.
   - Define Docker image, extensions, and settings.
   - Enable GitHub Codespaces support.

### 4. Release Management

Ship with confidence.

1. **Versioning**: Follow **SemVer** (MAJOR.MINOR.PATCH) and [Keep a Changelog](https://keepachangelog.com/).
2. **Workflows**:
   - **GitHub Flow**: Small teams, continuous delivery (`main` is stable).
   - **Git Flow**: Scheduled releases (`develop` + `release` branches).
   - **Forking**: Open source, distributed contributors.
3. **Process**: Bump version -> Update Changelog -> Tag -> Release.

## Self-Correction Checklist

- [ ] **License**: Is a `LICENSE` file present?
- [ ] **Readme**: Does `README.md` have installation instructions?
- [ ] **Contributing**: Is `CONTRIBUTING.md` clear?
- [ ] **Devcontainer**: Does `.devcontainer/devcontainer.json` exist?
- [ ] **SemVer**: Are releases using semantic versioning?
