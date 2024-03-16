# %% IMPORTS


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
    metric = metrics.SklearnMetric(name=name, greater_is_better=greater_is_better)
    # when
    score = metric.score(targets=targets, outputs=outputs)
    scorer = metric.scorer(model=model, inputs=inputs, targets=targets)
    # then
    assert low <= score <= high, "Score is not in the expected interval!"
    assert low <= scorer <= high, "Scorer is not in the expected interval!"
