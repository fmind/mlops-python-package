"""Test the searchers module."""
# pylint: disable=missing-docstring

# %% IMPORTS

import os

from wines import metrics, models, schemas, searchers

# %% SEARCHERS


def test_grid_cv_searcher(
    default_model: models.BaselineSklearnModel,
    default_metric: metrics.SklearnMetric,
    inputs: schemas.Inputs,
    target: schemas.Target,
    tmp_results_path: str,
):
    # given
    param_grid = {"max_depth": [3, 5, 7]}
    # when
    searcher = searchers.GridCVSearcher(param_grid=param_grid)
    result, best_params, best_score = searcher.search(
        model=default_model, metric=default_metric, inputs=inputs, target=target
    )
    searcher.save(path=tmp_results_path)
    # then
    assert len(result) == 3, "Results data should have the same length as the number of candidates!"
    assert set(best_params) == set(param_grid), "Best params should have the same keys as grid!"
    assert 0 <= best_score <= 1, "Best score should be between 0 and 1 for the given metric!"
    assert os.path.exists(tmp_results_path), "Results should be saved to the given path!"
