# pylint: disable=missing-docstring

# %% IMPORTS

from bikes import metrics, models, schemas, searchers, splitters

# %% SEARCHERS


def test_grid_cv_searcher(
    default_model: models.Model,
    default_metric: metrics.Metric,
    time_series_splitter: splitters.Splitter,
    inputs: schemas.Inputs,
    targets: schemas.Targets,
):
    # given
    param_grid = {"max_depth": [3, 5, 7]}
    searcher = searchers.GridCVSearcher(param_grid=param_grid)
    # when
    result, best_score, best_params = searcher.search(
        model=default_model, metric=default_metric, cv=time_series_splitter, inputs=inputs, targets=targets
    )
    # then
    assert set(best_params) == set(param_grid), "Best params should have the same keys as grid!"
    assert float("-inf") <= best_score <= float("+inf"), "Best score should be a floating number!"
    assert len(result) == sum(map(len, param_grid.values())), "Results should have one row per candidate!"
