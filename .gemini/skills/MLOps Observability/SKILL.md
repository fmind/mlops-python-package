---
name: MLOps Observability
description: Guide to implement full stack observability including reproducibility, lineage, monitoring, alerting, and explainability.
---

# MLOps Observability

## Goal

To implement a "Glass Box" system where every result is **Reproducible**, every asset has **Lineage**, and system health is **Monitored**, **Alerted** on, and **Explained**.

## Prerequisites

- **Language**: Python
- **Context**: Production monitoring and debugging.
- **Platform Suggestion**: MLflow, SHAP, Evidently, ...

## Instructions

### 1. Guarantee Reproducibility

Consistency is key. For instance:

1. **Randomness**: Set seeds for `random`, `numpy`, `torch`, `tensorflow`.
2. **Environment**: Use `docker` and locked dependencies (`uv.lock`).
3. **Builds**: Use `justfile` with `uv build --build-constraint` for deterministic wheels.
4. **Code**: Track git commit hash for every run.

### 2. Track Data Lineage

Know the origin of your data. For instance:

1. **Datasets**: Create MLflow Datasets with `mlflow.data.from_pandas`.
2. **Logging**: Log inputs to MLflow context with `mlflow.log_input`.
3. **Versioning**: Version data files (e.g., `data/v1.csv`) or use DVC.
4. **Transformations**: Log preprocessing parameters mapping data versions to model versions.

### 3. Monitoring & Drift Detection

Watch for silent failures. For instance:

1. **Validation**: Use `MLflow Evaluate` to gate models against quality thresholds.
2. **Drift**: Use `evidently` to compare `reference` (training) vs `current` (production) data.
   - Detect Data Drift (input distribution changes) and Concept Drift (relationship changes).
3. **System**: Enable MLflow System Metrics (`log_system_metrics=True`) for CPU/GPU.

### 4. Alerting

Don't stare at dashboards. For instance:

1. **Local**: Use `plyer` for desktop notifications during long training runs.
2. **Production**: Use `PagerDuty` (critical) or `Slack` (warnings).
3. **Thresholds**: Use Static (fixed value) or Dynamic (anomaly detection) rules.
4. **Action**: Alerts must link to a dashboard or playbook.

### 5. Explainability (XAI)

Trust but verify. For instance:

1. **Global**: Use Feature Importance (e.g., Random Forest) to understand overall logic.
2. **Local**: Use `SHAP` values to explain _individual_ predictions.
3. **Artifacts**: Save explanations (plots/tables) as MLflow artifacts.

### 6. Infrastructure & Costs

Optimize resources. For instance:

1. **Tags**: Tag runs with `project`, `env`, `user`.
2. **Costs**: Log `run_time` and instance type to estimate ROI.

## Self-Correction Checklist

- [ ] **Seeds**: Are random seeds fixed?
- [ ] **Inputs**: Are input datasets logged to MLflow?
- [ ] **System Metrics**: Is `log_system_metrics` enabled?
- [ ] **Explanations**: Are SHAP values generated?
- [ ] **Alerts**: Are thresholds defined for failures?
