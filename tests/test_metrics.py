"""Test the metrics module."""
# pylint: disable=missing-docstring

# %% IMPORTS

import typing as T

import pytest

from wines import metrics, models, schemas

# %% METRICS


@pytest.mark.parametrize(
    "greater_is_better, metric_name, interval",
    [
        (True, "accuracy_score", [0, 1]),
        (False, "balanced_accuracy_score", [-1, 0]),
    ],
)
def test_sklearn_metric(
    greater_is_better: bool,
    metric_name: str,
    interval: T.Tuple[int, int],
    default_model: models.Model,
    inputs: schemas.Inputs,
    target: schemas.Target,
    output: schemas.Output,
):
    # given
    low, high = interval
    # when
    metric = metrics.SklearnMetric(name=metric_name, greater_is_better=greater_is_better)
    score = metric.score(target=target, output=output)
    scorer = metric.scorer(model=default_model, inputs=inputs, target=target)
    # then
    assert low <= score <= high, "Score is not in the expected interval!"
    assert low <= scorer <= high, "Scorer is not in the expected interval!"
