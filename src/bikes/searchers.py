"""Find the best hyperparameters for a model."""

# %% IMPORTS

import abc
import typing as T

import pandas as pd
import pydantic as pdt
from sklearn import model_selection

from bikes import metrics, models, schemas, splitters

# %% TYPES

# results of a model search
# (results, best score, best params)
Results = tuple[pd.DataFrame, float, models.Params]

# cross-validation options for searchers
CrossValidation = int | splitters.Splits | splitters.Splitter

# %% SEARCHERS


class Searcher(abc.ABC, pdt.BaseModel):
    """Base class for a searcher."""

    # note: use searcher to tune models
    # e.g., to find the best model params

    KIND: str

    @abc.abstractmethod
    def search(
        self,
        model: models.Model,
        metric: metrics.Metric,
        cv: CrossValidation,
        inputs: schemas.Inputs,
        targets: schemas.Targets,
    ) -> Results:
        """Search the best model for the given inputs and targets."""


class GridCVSearcher(Searcher):
    """Grid searcher with cross-folds."""

    KIND: T.Literal["GridCVSearcher"] = "GridCVSearcher"

    # public
    param_grid: dict[str, list]
    n_jobs: int | None = None
    refit: bool = True
    verbose: int = 3
    error_score: str | float = "raise"
    return_train_score: bool = True

    def search(
        self,
        model: models.Model,
        metric: metrics.Metric,
        cv: CrossValidation,
        inputs: schemas.Inputs,
        targets: schemas.Targets,
    ) -> Results:
        """Search the best model for the given inputs and targets using a grid search."""
        searcher = model_selection.GridSearchCV(
            estimator=model,
            scoring=metric.scorer,
            cv=cv,
            param_grid=self.param_grid,
            n_jobs=self.n_jobs,
            refit=self.refit,
            verbose=self.verbose,
            error_score=self.error_score,
            return_train_score=self.return_train_score,
        )
        searcher.fit(inputs, targets)
        results = pd.DataFrame(searcher.cv_results_)
        return results, searcher.best_score_, searcher.best_params_


SearcherKind = GridCVSearcher
