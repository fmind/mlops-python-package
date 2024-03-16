"""Evaluate model performances with metrics."""

# %% IMPORTS

import abc
import typing as T

import pydantic as pdt
from sklearn import metrics

from bikes.core import models, schemas

# %% METRICS


class Metric(abc.ABC, pdt.BaseModel, strict=True, frozen=True, extra="forbid"):
    """Base class for a project metric.

    Use metrics to evaluate model performance.
    e.g., accuracy, precision, recall, MAE, F1, ...

    Parameters:
        name (str): name of the metric for the reporting.
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
            float: single result from the metric computation.
        """

    def scorer(
        self, model: models.Model, inputs: schemas.Inputs, targets: schemas.Targets
    ) -> float:
        """Score the model outputs against targets.

        Args:
            model (models.Model): model to evaluate.
            inputs (schemas.Inputs): model inputs values.
            targets (schemas.Targets): model expected values.

        Returns:
            float: single result from the metric computation.
        """
        outputs = model.predict(inputs=inputs)
        score = self.score(targets=targets, outputs=outputs)
        return score


class SklearnMetric(Metric):
    """Compute metrics with sklearn.

    Parameters:
        name (str): name of the sklearn metric.
        greater_is_better (bool): maximize or minimize.
    """

    KIND: T.Literal["SklearnMetric"] = "SklearnMetric"

    name: str = "mean_squared_error"
    greater_is_better: bool = False

    @T.override
    def score(self, targets: schemas.Targets, outputs: schemas.Outputs) -> float:
        metric = getattr(metrics, self.name)
        sign = 1 if self.greater_is_better else -1
        y_true = targets[schemas.TargetsSchema.cnt]
        y_pred = outputs[schemas.OutputsSchema.prediction]
        score = metric(y_pred=y_pred, y_true=y_true) * sign
        return float(score)


MetricKind = SklearnMetric
