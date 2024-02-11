"""Split dataframes into subsets."""

# %% IMPORTS

import abc
import typing as T

import numpy as np
import pydantic as pdt
from sklearn import model_selection

from bikes import schemas

# %% TYPES

Index = np.ndarray  # row index
TrainTest = tuple[Index, Index]
Splits = T.Iterator[TrainTest]

# %% SPLITTERS


class Splitter(abc.ABC, pdt.BaseModel):
    """Base class for a splitter."""

    # note: use splitters to split datasets
    # e.g., split between a train and test subsets

    # https://scikit-learn.org/stable/glossary.html#term-CV-splitter

    KIND: str

    @abc.abstractmethod
    def split(self, inputs: schemas.Inputs, targets: schemas.Targets, groups: list | None = None) -> Splits:
        """Split a dataframe into subsets."""

    @abc.abstractmethod
    def get_n_splits(self, inputs: schemas.Inputs, targets: schemas.Targets, groups: list | None = None) -> int:
        """Get the number of splits generated."""


class TrainTestSplitter(Splitter):
    """Split a dataframe into a train and test subsets."""

    KIND: T.Literal["TrainTestSplitter"] = "TrainTestSplitter"

    shuffle: bool = False  # required (time sensitive)
    test_size: int | float = 24 * 30 * 2  # 2 months
    random_state: int = 42

    def split(self, inputs: schemas.Inputs, targets: schemas.Targets, groups: list | None = None) -> Splits:
        """Split a dataframe into a train and test subsets."""
        index = np.arange(len(inputs))  # return integer position
        train_index, test_index = model_selection.train_test_split(
            index, shuffle=self.shuffle, test_size=self.test_size, random_state=self.random_state
        )
        yield train_index, test_index

    def get_n_splits(self, inputs: schemas.Inputs, targets: schemas.Targets, groups: list | None = None) -> int:
        """Get the unique train and test split."""
        return 1


class TimeSeriesSplitter(Splitter):
    """Split a dataframe into fixed time series subsets."""

    KIND: T.Literal["TimeSeriesSplitter"] = "TimeSeriesSplitter"

    gap: int = 0
    n_splits: int = 4
    test_size: int | float = 24 * 30 * 2  # 2 months

    def split(self, inputs: schemas.Inputs, targets: schemas.Targets, groups: list | None = None) -> Splits:
        """Split a dataframe into fixed time series subsets."""
        splitter = model_selection.TimeSeriesSplit(n_splits=self.n_splits, test_size=self.test_size)
        yield from splitter.split(inputs)

    def get_n_splits(self, inputs: schemas.Inputs, targets: schemas.Targets, groups: list | None = None) -> int:
        """Get the number time series splits."""
        return self.n_splits


SplitterKind = TrainTestSplitter | TimeSeriesSplitter
