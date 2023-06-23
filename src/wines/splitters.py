"""Split a dataframe into subsets."""

# %% IMPORTS

import abc
import typing as T

import pandas as pd
import pydantic as pdt
from sklearn import model_selection

# %% SPLITTERS


class Splitter(abc.ABC, pdt.BaseModel):
    """Base class for a splitter."""

    # note: use splitters to split datasets
    # e.g., split between a train and test set

    KIND: str

    @abc.abstractmethod
    def split(self, data: pd.DataFrame) -> T.Tuple[pd.DataFrame, ...]:
        """Split a dataframe into several subsets."""


class TrainTestSplitter(Splitter):
    """Split a dataframe into a train and test sets."""

    KIND: T.Literal["TrainTestSplitter"] = "TrainTestSplitter"

    ratio: float = 0.8
    shuffle: bool = True
    random_state: int = 42

    def split(self, data: pd.DataFrame) -> T.Tuple[pd.DataFrame, pd.DataFrame]:
        """Split a dataframe into a train and test sets."""
        train, test = model_selection.train_test_split(
            data, shuffle=self.shuffle, train_size=self.ratio, random_state=self.random_state
        )
        return train, test


# alias to all splitter kinds
# note: convert to Union with 2+ types
SplitterKind = TrainTestSplitter
