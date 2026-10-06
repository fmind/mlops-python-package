"""Model code that MLflow runs to rebuild the PyFunc adapter of project models.

MLflow copies this file next to each model logged by `CustomSaver` and executes it on
load, so the adapter is defined by code instead of being pickled.

https://mlflow.org/docs/latest/ml/model/models-from-code/
"""

# %% IMPORTS

import mlflow

from bikes.io import registries

# %% MODELS

ADAPTER = registries.CustomSaver.Adapter()

mlflow.models.set_model(ADAPTER)
