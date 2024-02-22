"""Find the best hyperparameters for a model."""

# %% IMPORTS

import abc
import typing as T

import pandas as pd
import pydantic as pdt
from sklearn import model_selection

from bikes import metrics, models, schemas, splitters

# %% TYPES

# Grid of model params
# {param name -> param values}
Grid = dict[str, list[T.Any]]

# results of a model search
# (results, best score, best params)
Results = tuple[pd.DataFrame, float, models.Params]

# cross-validation options for searchers
CrossValidation = int | splitters.Splits | splitters.Splitter

# %% SEARCHERS


class Searcher(abc.ABC, pdt.BaseModel, strict=True):
    """Base class for a searcher.

    note: use searcher to tune models.
    e.g., to find the best model params.
    """

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
        """Search the best model for the given inputs and targets.

        Args:
            model (models.Model): machine learning model to tune.
            metric (metrics.Metric): main metric to optimize.
            cv (CrossValidation): structure for cross-fold.
            inputs (schemas.Inputs): model inputs for tuning.
            targets (schemas.Targets): model targets for tuning.

        Returns:
            Results: all the results of the tuning process.
        """


class GridCVSearcher(Searcher):
    """Grid searcher with cross-folds.

    Attributes:
        param_grid (Grid): mapping of param key -> values.
        n_jobs (int, optional): number of jobs to run in parallel.
        refit (bool): refit the model after the tuning.
        verbose (int): set the search verbosity level.
        error_score (str | float): strategy or value on error.
        return_train_score (bool): include train scores.
    """

    KIND: T.Literal["GridCVSearcher"] = "GridCVSearcher"

    # public
    param_grid: Grid
    n_jobs: int | None = None
    refit: bool = False
    verbose: int = 3
    error_score: str | float = "raise"
    return_train_score: bool = False

    @T.override
    def search(
        self,
        model: models.Model,
        metric: metrics.Metric,
        cv: CrossValidation,
        inputs: schemas.Inputs,
        targets: schemas.Targets,
    ) -> Results:
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
