# %% IMPORTS

import mlflow
import pandas as pd
import pytest
from bikes.core import metrics, models, schemas

# %% METRICS


@pytest.mark.parametrize(
    "name, interval, greater_is_better",
    [
        ("mean_squared_error", [0, float("inf")], True),
        ("mean_absolute_error", [float("-inf"), 0], False),
    ],
)
def test_sklearn_metric(
    name: str,
    interval: tuple[int, int],
    greater_is_better: bool,
    model: models.Model,
    inputs: schemas.Inputs,
    targets: schemas.Targets,
    outputs: schemas.Outputs,
) -> None:
    # given
    low, high = interval
    data = pd.concat([targets, outputs], axis="columns")
    metric = metrics.SklearnMetric(name=name, greater_is_better=greater_is_better)
    # when
    score = metric.score(targets=targets, outputs=outputs)
    scorer = metric.scorer(model=model, inputs=inputs, targets=targets)
    mlflow_metric = metric.to_mlflow()
    mlflow_results = mlflow.evaluate(
        data=data,
        predictions=schemas.OutputsSchema.prediction,
        targets=schemas.TargetsSchema.cnt,
        extra_metrics=[mlflow_metric],
    )
    # then
    # - score
    assert low <= score <= high, "Score should be in the expected interval!"
    # - scorer
    assert low <= scorer <= high, "Scorer should be in the expected interval!"
    # - mlflow metric
    assert mlflow_metric.name == metric.name, "Mlflow metric name should be the same!"
    assert (
        mlflow_metric.greater_is_better == metric.greater_is_better
    ), "Mlflow metric greater is better should be the same!"
    # - mlflow results
    assert mlflow_results.metrics == {
        metric.name: score * (1 if greater_is_better else -1)
    }, "Mlflow results metrics should have the same name and score!"


# %% THRESHOLDS


def test_threshold() -> None:
    # given
    threshold = metrics.Threshold(threshold=10, greater_is_better=True)
    # when
    mlflow_threshold = threshold.to_mlflow()
    # then
    assert mlflow_threshold.threshold == threshold.threshold, "Threshold should be the same!"
    assert (
        mlflow_threshold.greater_is_better == threshold.greater_is_better
    ), "Greater is better should be the same!"
