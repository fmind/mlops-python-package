# %% IMPORTS

from regression_model_template.core import metrics, models, schemas
from regression_model_template.utils import searchers, splitters

# %% SEARCHERS


def test_grid_cv_searcher(
    model: models.Model,
    metric: metrics.Metric,
    inputs: schemas.Inputs,
    targets: schemas.Targets,
    train_test_splitter: splitters.Splitter,
) -> None:
    # given
    param_grid = {"max_depth": [3, 5, 7]}
    searcher = searchers.GridCVSearcher(param_grid=param_grid)
    # when
    result, best_score, best_params = searcher.search(
        model=model, metric=metric, inputs=inputs, targets=targets, cv=train_test_splitter
    )
    # then
    assert set(best_params) == set(param_grid), "Best params should have the same keys as grid!"
    assert float("-inf") < best_score < float("+inf"), "Best score should be a floating number!"
    assert len(result) == sum(len(vs) for vs in param_grid.values()), "Results should have one row per candidate!"
