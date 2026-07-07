---
name: MLOps Prototyping
description: Guide to create structured, reproducible Jupyter notebooks for MLOps prototyping, emphasizing configuration management and pipeline integrity.
---

# MLOps Prototyping

## Goal

To create standardized, reproducible, and production-ready prototypes in Jupyter notebooks. This skill enforces a structured layout (Imports -> Configs -> Load -> EDA -> Modeling -> Eval) and robust engineering practices (Pipelines, Split-Verification) to prevent technical debt and data leakage.

## Prerequisites

- **Language**: Python
- **Environment**: `uv` managed project (`.venv`)
- **Context**: Executed within a `.ipynb` file or converting to one.

## Instructions

### 1. Notebook Structure

Enforce the following linear sections in every notebook to ensure readability and maintainability.

1. **Title & Purpose**: H1 Title and a brief description of the experiment goals.
2. **Imports**: Group standard libraries, third-party, and usage-specific imports.
3. **Configs**: Define **Global Constants** (paths, random seeds, hyperparameters) here. No magic numbers deeper in the code.
4. **Datasets**: Load, validate, and split data.
5. **Analysis (EDA)**: Inspect target distributions and correlations.
6. **Modeling**: Define and train `sklearn.pipeline.Pipeline` objects.
7. **Evaluations**: Compute metrics and visualize performance on held-out data.

### 2. Configuration Standards

Expose all "knobs" at the top of the notebook for easy experimentation.

- **Randomness**: Define `RANDOM_STATE = 42` and use it in splits and model initialization.
- **Paths**: Use `pathlib` for robust path handling.

  ```python
  from pathlib import Path
  ROOT = Path("..")
  DATA_PATH = ROOT / "data" / "input.parquet"
  ```

- **Hyperparameters**: Group model params (e.g., `N_ESTIMATORS`, `MAX_DEPTH`).
- **Toggles**: Use booleans for expensive operations (e.g., `USE_GPU = True`, `RUN_GRID_SEARCH = False`).

### 3. Data Management

Ensure data integrity and prevent leakage.

- **Loading**: Prefer `pd.read_parquet` for speed/types, or `pd.read_csv`.
- **Splitting**:
  - **Always** split into `X_train`, `X_test`, `y_train`, `y_test` **before** any data-dependent transformations (imputation, scaling).
  - **Random Split**: Use `sklearn.model_selection.train_test_split` with `stratify` for balanced classification.
  - **Time Series**: Use `sklearn.model_selection.TimeSeriesSplit` if data has a temporal dimension (do NOT shuffle).
  - Use `random_state=RANDOM_STATE`.

### 4. Pipeline Construction

Prohibit raw data transformations on the full dataset.

- **Mandate**: Use `sklearn.pipeline.Pipeline` or `ColumnTransformer`.
- **Why**: Automation of `fit` on train and `transform` on test prevents data leakage.
- **Example**:

  ```python
  from sklearn.pipeline import Pipeline
  from sklearn.preprocessing import StandardScaler, OneHotEncoder
  from sklearn.impute import SimpleImputer
  from sklearn.compose import ColumnTransformer

  CACHE = "./.cache" # Define a cache directory

  numeric_transformer = Pipeline(steps=[
      ('imputer', SimpleImputer(strategy='median')),
      ('scaler', StandardScaler())
  ])

  preprocessor = ColumnTransformer(transformers=[
      ('num', numeric_transformer, numeric_features)
  ])

  # Use 'memory' to cache transformer outputs, speeding up GridSearch
  model = Pipeline(steps=[
      ('preprocessor', preprocessor),
      ('classifier', RandomForestClassifier())
  ], memory=CACHE)
  ```

### 5. Evaluation & Visualization

Go beyond accuracy/MSE.

- **Metrics**: Use `sklearn.metrics` appropriate for the task (F1, ROC-AUC, RMSE, MAE).
- **Baselines**: Compare against a "Dummy" model (mean/mode) to verify learning.
- **Visualization**:
  - **Regression**: Residual plots, Actual vs Predicted.
  - **Classification**: Confusion Matrix, ROC Curve, Precision-Recall.
  - **Feature Importance**: Visualize `feature_importances_` or SHAP values.

### 6. Transition to Production

Facilitate the move from notebook to python package (`src/`).

- **Function Refactoring**: Once a block of code is stable (e.g., a complex data cleaning step), refactor it into a function _within_ the notebook. This makes moving it to a `.py` file trivial later.
- **Cell Tagging**: Use tags like `parameters` (for Papermill) or `export` to mark cells that should be part of the final documentation or automated pipeline.
- **Clean State**: Ensure the notebook runs top-to-bottom (`Restart Kernel and Run All`) without errors before committing.

## Self-Correction Checklist

- [ ] **No Magic Numbers**: Are all parameters in the `Configs` section?
- [ ] **No Data Leakage**: Is `fit` called ONLY on `X_train`?
- [ ] **Reproducibility**: Is `random_state` set for all stochastic operations?
- [ ] **Resilience**: are paths defined relative to the project root?
- [ ] **Clarity**: Does the notebook read like a report (Markdown cells explaining the _Why_)?
