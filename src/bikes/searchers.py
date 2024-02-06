"""Find the best hyperparameters for a model."""

# %% IMPORTS

import abc
import typing as T

import pandas as pd
import pydantic as pdt
from sklearn import model_selection

from bikes import metrics, models, schemas

# %% TYPINGS

# grid of model params
# {param name -> [param values]}
Grid = dict[str, list[T.Any]]

# results of a model search
# (results, best params, best score)
Results = tuple[pd.DataFrame, models.Params, float]

# %% SEARCHERS


class Searcher(abc.ABC, pdt.BaseModel):
    """Base class for a searcher."""

    # note: use searcher to tune models
    # e.g., to find the best model params

    KIND: str

    @abc.abstractmethod
    def search(
        self, model: models.Model, metric: metrics.Metric, inputs: schemas.Inputs, targets: schemas.Targets
    ) -> Results:
        """Search the best model for the given inputs and targets."""


class GridCVSearcher(Searcher):
    """Grid searcher with cross-folds."""

    KIND: T.Literal["GridCVSearcher"] = "GridCVSearcher"

    # public
    param_grid: Grid
    n_jobs: int | None = None
    refit: bool = True
    cv: int = 3
    verbose: int = 3
    error_score: str | float = "raise"
    return_train_score: bool = True

    def search(
        self, model: models.Model, metric: metrics.Metric, inputs: schemas.Inputs, targets: schemas.Targets
    ) -> Results:
        """Search the best model for the given inputs and targets using a grid search with cross-validation."""
        searcher = model_selection.GridSearchCV(
            estimator=model,
            scoring=metric.scorer,
            param_grid=self.param_grid,
            n_jobs=self.n_jobs,
            refit=self.refit,
            cv=self.cv,
            verbose=self.verbose,
            error_score=self.error_score,
            return_train_score=self.return_train_score,
        )
        searcher.fit(inputs, targets)
        results = pd.DataFrame(searcher.cv_results_)
        return results, searcher.best_params_, searcher.best_score_


SearcherKind = GridCVSearcher
