"""Read/Write datasets from/to external sources/destinations."""

# %% IMPORTS

import abc
import typing as T

import pandas as pd
import pydantic as pdt

# %% READERS


class Reader(abc.ABC, pdt.BaseModel, strict=True):
    """Base class for a dataset reader."""

    # note: use reader to load data in memory
    # e.g., to read file, database, cloud storage, ...

    KIND: str

    limit: int | None = None

    @abc.abstractmethod
    def read(self) -> pd.DataFrame:
        """Read a dataframe from a dataset."""


class ParquetReader(Reader):
    """Read a dataframe from a parquet file."""

    KIND: T.Literal["ParquetReader"] = "ParquetReader"

    path: str

    def read(self) -> pd.DataFrame:
        """Read a dataframe from a parquet dataset."""
        return pd.read_parquet(self.path).head(self.limit)


ReaderKind = ParquetReader

# %% WRITERS


class Writer(abc.ABC, pdt.BaseModel, strict=True):
    """Base class for a dataset writer."""

    # note: use writer to save data from memory
    # e.g., to write file, database, cloud storage, ...

    KIND: str

    @abc.abstractmethod
    def write(self, data: pd.DataFrame) -> None:
        """Write a dataframe to a dataset."""


class ParquetWriter(Writer):
    """Writer a dataframe to a parquet file."""

    KIND: T.Literal["ParquetWriter"] = "ParquetWriter"

    path: str

    def write(self, data: pd.DataFrame) -> None:
        """Write a dataframe to a parquet dataset."""
        pd.DataFrame.to_parquet(data, self.path)


WriterKind = ParquetWriter
