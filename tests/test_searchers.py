"""Test the searchers module."""

# pylint: disable=missing-docstring

# %% IMPORTS

from bikes import metrics, models, schemas, searchers

# %% SEARCHERS


def test_grid_cv_searcher(
    default_model: models.BaselineSklearnModel,
    default_metric: metrics.SklearnMetric,
    inputs: schemas.Inputs,
    targets: schemas.Targets,
):
    # given
    param_grid = {"max_depth": [3, 5, 7]}
    # when
    searcher = searchers.GridCVSearcher(param_grid=param_grid)
    result, best_params, best_score = searcher.search(
        model=default_model, metric=default_metric, inputs=inputs, targets=targets
    )
    # then
    assert set(best_params) == set(param_grid), "Best params should have the same keys as grid!"
    assert float("-inf") <= best_score <= float("+inf"), "Best score should be a floating number!"
    assert len(result) == len(param_grid["max_depth"]), "Results should have one row per candidate!"
