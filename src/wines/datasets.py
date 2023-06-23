"""Read/Write datasets from/to external sources."""

# %% IMPORTS

import abc
import typing as T

import pandas as pd
import pydantic as pdt

# %% DATASETS


class Dataset(abc.ABC, pdt.BaseModel):
    """Base class for a dataset."""

    # note: use datasets to manage the IO
    # e.g., to read/write from/to a source/dest

    KIND: str

    @abc.abstractmethod
    def read(self) -> pd.DataFrame:
        """Read a dataframe from a dataset."""

    @abc.abstractmethod
    def write(self, data: pd.DataFrame) -> None:
        """Write a dataframe to a dataset."""


class ParquetDataset(Dataset):
    """Read/Write a pandas dataframe from/to a parquet file."""

    KIND: T.Literal["ParquetDataset"] = "ParquetDataset"

    path: str  # support local / remote
    read_kwargs: T.Dict[str, T.Any] = {}
    write_kwargs: T.Dict[str, T.Any] = {}

    def read(self) -> pd.DataFrame:
        """Read a pandas dataframe from a parquet dataset."""
        return pd.read_parquet(self.path, **self.read_kwargs)

    def write(self, data: pd.DataFrame) -> None:
        """Write a pandas dataframe to a parquet dataset."""
        pd.DataFrame.to_parquet(data, self.path, **self.write_kwargs)


# alias to all dataset kinds
# note: convert to Union with 2+ types
DatasetKind = ParquetDataset
