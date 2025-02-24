"""Find the best hyperparameters for a model."""

# %% IMPORTS

import abc
import typing as T

import pandas as pd
import pydantic as pdt
from sklearn import model_selection

from regression_model_template.core import metrics, models, schemas
from regression_model_template.utils import splitters

# %% TYPES

# Grid of model params
Grid = dict[models.ParamKey, list[models.ParamValue]]

# Results of a model search
Results = tuple[
    T.Annotated[pd.DataFrame, "details"],
    T.Annotated[float, "best score"],
    T.Annotated[models.Params, "best params"],
]

# Cross-validation options for searchers
CrossValidation = int | splitters.TrainTestSplits | splitters.Splitter

# %% SEARCHERS


class Searcher(abc.ABC, pdt.BaseModel, strict=True, frozen=True, extra="forbid"):
    """Base class for a searcher.

    Use searcher to fine-tune models.
    i.e., to find the best model params.

    Parameters:
        param_grid (Grid): mapping of param key -> values.
    """

    KIND: str

    param_grid: Grid

    @abc.abstractmethod
    def search(
        self,
        model: models.Model,
        metric: metrics.Metric,
        inputs: schemas.Inputs,
        targets: schemas.Targets,
        cv: CrossValidation,
    ) -> Results:
        """Search the best model for the given inputs and targets.

        Args:
            model (models.Model): AI/ML model to fine-tune.
            metric (metrics.Metric): main metric to optimize.
            inputs (schemas.Inputs): model inputs for tuning.
            targets (schemas.Targets): model targets for tuning.
            cv (CrossValidation): choice for cross-fold validation.

        Returns:
            Results: all the results of the searcher execution process.
        """


class GridCVSearcher(Searcher):
    """Grid searcher with cross-fold validation.

    Convention: metric returns higher values for better models.

    Parameters:
        n_jobs (int, optional): number of jobs to run in parallel.
        refit (bool): refit the model after the tuning.
        verbose (int): set the searcher verbosity level.
        error_score (str | float): strategy or value on error.
        return_train_score (bool): include train scores if True.
    """

    KIND: T.Literal["GridCVSearcher"] = "GridCVSearcher"

    n_jobs: int | None = None
    refit: bool = True
    verbose: int = 3
    error_score: str | float = "raise"
    return_train_score: bool = False

    @T.override
    def search(
        self,
        model: models.Model,
        metric: metrics.Metric,
        inputs: schemas.Inputs,
        targets: schemas.Targets,
        cv: CrossValidation,
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
