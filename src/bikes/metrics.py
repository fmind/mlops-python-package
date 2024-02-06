"""Evaluate model performance with metrics."""

# %% IMPORTS

import abc
import typing as T

import pydantic as pdt
from sklearn import metrics

from bikes import models, schemas

# %% METRICS


class Metric(abc.ABC, pdt.BaseModel):
    """Base class for a metric."""

    # note: use metrics to evaluate models
    # e.g., accuracy, precision, recall, f1, ...

    KIND: str

    @abc.abstractmethod
    def score(self, targets: schemas.Targets, outputs: schemas.Outputs) -> float:
        """Score the outputs against the targets."""

    def scorer(self, model: models.Model, inputs: schemas.Inputs, targets: schemas.Targets) -> float:
        """Score the model outputs against the targets."""
        outputs = model.predict(inputs=inputs)  # prediction
        score = self.score(targets=targets, outputs=outputs)
        return score


class SklearnMetric(Metric):
    """Compute metrics with sklearn."""

    KIND: T.Literal["SklearnMetric"] = "SklearnMetric"

    name: str = "mean_squared_error"
    greater_is_better: bool = False

    def score(self, targets: schemas.Targets, outputs: schemas.Outputs) -> float:
        """Score the outputs against the targets with sklearn."""
        metric = getattr(metrics, self.name)
        sign = 1 if self.greater_is_better else -1
        targets = targets[schemas.TargetsSchema.cnt]
        outputs = outputs[schemas.OutputsSchema.prediction]
        score = metric(y_pred=outputs, y_true=targets)
        return score * sign


MetricKind = SklearnMetric
