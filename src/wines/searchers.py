"""Find the best hyperparameters for a model."""

# %% IMPORTS

import abc
import typing as T

import pandas as pd
import pydantic as pdt
from sklearn import model_selection

from wines import metrics, models, schemas

# %% TYPINGS

# grid of model params
# {param name -> [param values]}
Grid = T.Dict[str, T.List[T.Any]]

# results of a model search
# (results, best params, best score)
Results = T.Tuple[pd.DataFrame, models.Params, float]

# %% SEARCHERS


class Searcher(abc.ABC, pdt.BaseModel):
    """Base class for a searcher."""

    # note: use searcher to tune models
    # e.g., to find the best model params

    class Config:
        """Default pydantic config."""

        underscore_attrs_are_private = True

    KIND: str

    @abc.abstractmethod
    def search(
        self, model: models.Model, metric: metrics.Metric, inputs: schemas.Inputs, target: schemas.Target
    ) -> Results:
        """Search the best model for the given inputs and target."""

    @abc.abstractmethod
    def save(self, path: str) -> None:
        """Save the searcher results to the given path."""


class GridCVSearcher(Searcher):
    """Grid searcher with cross-folds."""

    KIND: T.Literal["GridCVSearcher"] = "GridCVSearcher"

    # public
    param_grid: Grid
    n_jobs: T.Optional[int] = None
    refit: bool = True
    cv: int = 3
    verbose: int = 3
    error_score: T.Union[str, float] = "raise"
    return_train_score: bool = True
    # private
    _results: T.Optional[pd.DataFrame] = None
    _searcher: T.Optional[model_selection.GridSearchCV] = None

    def search(
        self, model: models.Model, metric: metrics.Metric, inputs: schemas.Inputs, target: schemas.Target
    ) -> Results:
        """Search the best model for the given inputs and target using a grid search with CV."""
        self._searcher = model_selection.GridSearchCV(
            scoring=metric.scorer,
            estimator=model,
            param_grid=self.param_grid,
            n_jobs=self.n_jobs,
            refit=self.refit,
            cv=self.cv,
            verbose=self.verbose,
            error_score=self.error_score,
            return_train_score=self.return_train_score,
        )
        self._searcher.fit(inputs, target)
        self._results = pd.DataFrame(self._searcher.cv_results_)
        return self._results, self._searcher.best_params_, self._searcher.best_score_

    def save(self, path: str) -> None:
        """Save the griv CV searcher results to the given path."""
        assert self._results is not None, "No results to save. Call the search() method first!"
        self._results.to_csv(path)


# alias to all searcher kinds
# note: convert to Union with 2+ types
SearcherKind = GridCVSearcher
