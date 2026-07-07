---
name: MLOps Industrialization
description: Guide to transform prototypes into robust, distributable Python packages using the src layout, hybrid paradigm, and strict configuration management.
---

# MLOps Coding - Productionizing Skill

## Goal

To convert experimental code (notebooks/scripts) into a high-quality, distributable Python package. This skill enforces the **src/ layout**, a **Hybrid Paradigm** (OOP structure + Functional purity), and **Strict Configuration** to ensure scalability, security, and maintainability.

## Prerequisites

- **Language**: Python
- **Manager**: `uv`
- **Context**: Moving from `notebooks/` to `src/`.

## Instructions

### 1. Packaging Structure (`src` Layout)

Adopt the `src` layout to prevent import errors and separate source from tooling.

1. **Directory Tree**:

   ```text
   my-project/
   ├── pyproject.toml       # Dependencies & Metadata
   ├── uv.lock
   ├── README.md
   └── src/
       └── my_package/      # Main package directory
           ├── __init__.py
           ├── io/          # Side-effects (Datasets, APIs)
           ├── domain/      # Pure business logic (Models, Features)
           └── application/ # Orchestration (Training loops, Inference)
   ```

2. **Configuration**: Use `pyproject.toml` for all build metadata and dependencies.

### 2. Modularity & Paradigm (Hybrid Style)

Balance structure with predictability.

1. **Domain Layer (Pure)**:
   - **Rule**: Code here must be deterministic and free of side effects (no I/O).
   - **Use Case**: Feature transformations, Model architecture definitions.
   - **Style**: Functional (pure functions) or Immutable Objects (dataclasses).
2. **I/O Layer (Impure)**:
   - **Rule**: Isolate external interactions here.
   - **Use Case**: Loading data from S3, saving models to disk, logging to MLflow.
   - **Style**: OOP (Classes to manage connections/state).
3. **Application Layer (Orchestration)**:
   - **Rule**: Wire Domain and I/O together.
   - **Use Case**: Tuning, Training, Inference, Evaluation, etc.

### 3. Application Entrypoints

Create standard, installable CLI tools.

1. **Define Script**: Create `src/my_package/scripts.py` with a `main()` function.
2. **Register**: Add to `pyproject.toml`:

   ```toml
   [project.scripts]
   my-tool = "my_package.scripts:main"
   ```

3. **CLI Execution**:
   - **Dev**: `uv run my-tool` (No install needed).
   - **Prod**: `pip install .` -> `my-tool` (Installed on PATH).
4. **Guard**: Always use `if __name__ == "__main__":` in scripts to prevent execution on import.

### 4. Configuration Management

Decouple settings from code using **OmegaConf** (Parsing) and **Pydantic** (Validation).

1. **Define Schema (Pydantic)**:
   - Create a class that defines _expected_ types and defaults.

   ```python
   from pydantic import BaseModel

   class TrainingConfig(BaseModel):
       batch_size: int = 32
       learning_rate: float = 0.001
       use_gpu: bool = False
   ```

2. **Parse & Validate (OmegaConf)**:
   - Load YAML, merge with CLI args, and validate against the schema.

   ```python
   import omegaconf

   # 1. Load YAML
   conf = omegaconf.OmegaConf.load("config.yaml")
   # 2. Merge with CLI (optional)
   cli_conf = omegaconf.OmegaConf.from_cli()
   merged = omegaconf.OmegaConf.merge(conf, cli_conf)
   # 3. Validate -> Returns a validated Pydantic object
   cfg: TrainingConfig = TrainingConfig(**omegaconf.OmegaConf.to_container(merged))
   ```

3. **Secrets**: Use Environment Variables (`os.getenv`), never commit them.

### 5. Documentation & Quality

Make code usable and maintainable.

1. **Docstrings**: Use **Google Style** docstrings for all modules, classes, and functions.

   ```python
   def calculate_metric(y_true: np.ndarray, y_pred: np.ndarray) -> float:
       """Calculates the accuracy score.

       Args:
           y_true: Ground truth labels.
           y_pred: Predicted labels.

       Returns:
           The accuracy as a float between 0 and 1.
       """
   ```

2. **Type Hints**: Use standard python typing (`typing`, `list[str]`) everywhere.

### 6. Best Practices Summary

- **Config != Code**: Never hardcode paths or hyperparams; use the `Pydantic + OmegaConf` pattern.
- **Entrypoints are APIs**: Design your CLI (`[project.scripts]`) as the public interface for your automation tools.
- **Immutable Core**: Keep your domain logic side-effect free; push I/O to the edges.

## Self-Correction Checklist

- [ ] **No Side Effects on Import**: Does `import my_package` run any code? (It shouldn't).
- [ ] **Src Layout**: Is code inside `src/`?
- [ ] **Config Safety**: Are secrets excluded from `pyproject.toml` and YAML?
- [ ] **Typing**: Are function signatures fully type-hinted?
- [ ] **Entrypoints**: Is the CLI registered in `pyproject.toml`?
