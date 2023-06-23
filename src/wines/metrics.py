"""Evaluate the model performance with metrics."""

# %% IMPORTS

import abc
import typing as T

import pydantic as pdt
from sklearn import metrics

from wines import models, schemas

# %% METRICS


class Metric(abc.ABC, pdt.BaseModel):
    """Base class for a metric."""

    # note: use metrics to evaluate models
    # e.g., accuracy, precision, recall, f1, ...

    KIND: str

    @abc.abstractmethod
    def score(self, target: schemas.Target, output: schemas.Output) -> float:
        """Score the output against the target."""

    def scorer(self, model: models.Model, inputs: schemas.Inputs, target: schemas.Target) -> float:
        """Score the model output against the target."""
        output = model.predict(inputs=inputs)  # prediction
        score = self.score(target=target, output=output)
        return score


class SklearnMetric(Metric):
    """Compute metrics with sklearn."""

    KIND: T.Literal["SklearnMetric"] = "SklearnMetric"

    name: str = "accuracy_score"
    greater_is_better: bool = True

    def score(self, target: schemas.Target, output: schemas.Output) -> float:
        """Score the output against the target with sklearn."""
        metric = getattr(metrics, self.name)
        sign = 1 if self.greater_is_better else -1
        score = metric(target["target"], output["output"]) * sign
        return score


# alias to all metric kinds
# note: convert to Union with 2+ types
MetricKind = SklearnMetric
