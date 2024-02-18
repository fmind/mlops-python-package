"""Evaluate model performance with metrics."""

# %% IMPORTS

import abc
import typing as T

import pydantic as pdt
from sklearn import metrics

from bikes import models, schemas

# %% METRICS


class Metric(abc.ABC, pdt.BaseModel, strict=True):
    """Base class for a metric.

    Use metrics to evaluate model performance.
    e.g., accuracy, precision, recall, mae, f1, ...

    Attributes:
        name: name of the metric.
    """

    KIND: str

    name: str

    @abc.abstractmethod
    def score(self, targets: schemas.Targets, outputs: schemas.Outputs) -> float:
        """Score the outputs against the targets.

        Args:
            targets (schemas.Targets): expected values.
            outputs (schemas.Outputs): predicted values.

        Returns:
            float: metric result.
        """

    def scorer(self, model: models.Model, inputs: schemas.Inputs, targets: schemas.Targets) -> float:
        """Score the model outputs against the targets.

        Args:
            model (models.Model): model to evaluate.
            inputs (schemas.Inputs): model inputs values.
            targets (schemas.Targets): model expected values.

        Returns:
            float: metric result.
        """
        outputs = model.predict(inputs=inputs)  # prediction
        score = self.score(targets=targets, outputs=outputs)
        return score


class SklearnMetric(Metric):
    """Compute metrics with sklearn.

    Attributes:
        name: name of the sklearn metric.
        greater_is_better: maximize or minimize.
    """

    KIND: T.Literal["SklearnMetric"] = "SklearnMetric"

    name: str = "mean_squared_error"
    greater_is_better: bool = False

    @T.override
    def score(self, targets: schemas.Targets, outputs: schemas.Outputs) -> float:
        metric = getattr(metrics, self.name)
        sign = 1 if self.greater_is_better else -1
        targets = targets[schemas.TargetsSchema.cnt]
        outputs = outputs[schemas.OutputsSchema.prediction]
        score = metric(y_pred=outputs, y_true=targets) * sign
        return score


MetricKind = SklearnMetric
