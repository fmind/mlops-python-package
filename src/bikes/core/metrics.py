"""Evaluate model performances with metrics."""

# %% IMPORTS

from __future__ import annotations

import abc
import typing as T

import mlflow
import pandas as pd
import pydantic as pdt
from sklearn import metrics

from bikes.core import models, schemas

# %% TYPINGS

MlflowMetric: T.TypeAlias = mlflow.metrics.MetricValue
MlflowThreshold: T.TypeAlias = mlflow.models.MetricThreshold
MlflowModelValidationFailedException: T.TypeAlias = (
    mlflow.models.evaluation.validation.ModelValidationFailedException
)

# %% METRICS


class Metric(abc.ABC, pdt.BaseModel, strict=True, frozen=True, extra="forbid"):
    """Base class for a project metric.

    Use metrics to evaluate model performance.
    e.g., accuracy, precision, recall, MAE, F1, ...

    Parameters:
        name (str): name of the metric for the reporting.
        greater_is_better (bool): maximize or minimize result.
    """

    KIND: str

    name: str
    greater_is_better: bool

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
        """Score model outputs against targets.

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

    def to_mlflow(self) -> MlflowMetric:
        """Convert the metric to an Mlflow metric.

        Returns:
            MlflowMetric: the Mlflow metric.
        """

        def eval_fn(predictions: pd.Series[int], targets: pd.Series[int]) -> MlflowMetric:
            """Evaluation function associated with the mlflow metric.

            Args:
                predictions (pd.Series): model predictions.
                targets (pd.Series | None): model targets.

            Returns:
                MlflowMetric: the mlflow metric.
            """
            score_targets = schemas.Targets(
                {schemas.TargetsSchema.cnt: targets}, index=targets.index
            )
            score_outputs = schemas.Outputs(
                {schemas.OutputsSchema.prediction: predictions}, index=predictions.index
            )
            sign = 1 if self.greater_is_better else -1  # reverse the effect
            score = self.score(targets=score_targets, outputs=score_outputs)
            return MlflowMetric(aggregate_results={self.name: score * sign})

        return mlflow.metrics.make_metric(
            eval_fn=eval_fn, name=self.name, greater_is_better=self.greater_is_better
        )


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

# %% THRESHOLDS


class Threshold(abc.ABC, pdt.BaseModel, strict=True, frozen=True, extra="forbid"):
    """A project threshold for a metric.

    Use thresholds to monitor model performances.
    e.g., to trigger an alert when a threshold is met.

    Parameters:
        threshold (int | float): absolute threshold value.
        greater_is_better (bool): maximize or minimize result.
    """

    threshold: int | float
    greater_is_better: bool

    def to_mlflow(self) -> MlflowThreshold:
        """Convert the threshold to an mlflow threshold.

        Returns:
            MlflowThreshold: the mlflow threshold.
        """
        return MlflowThreshold(threshold=self.threshold, greater_is_better=self.greater_is_better)
