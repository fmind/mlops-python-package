"""Read/Write datasets from/to external sources/destinations."""

# %% IMPORTS

import abc
import typing as T

import pandas as pd
import pydantic as pdt

# %% READERS


class Reader(abc.ABC, pdt.BaseModel, strict=True):
    """Base class for a dataset reader.

    Use a reader to load a dataset in memory.
    e.g., to read file, database, cloud storage, ...

    Attributes:
        limit: maximum number of rows to read from dataset.
    """

    KIND: str

    limit: int | None = None

    @abc.abstractmethod
    def read(self) -> pd.DataFrame:
        """Read a dataframe from a dataset.

        Returns:
            pd.DataFrame: dataframe representation.
        """


class ParquetReader(Reader):
    """Read a dataframe from a parquet file.

    Attributes:
        path: local or remote path to a dataset.
    """

    KIND: T.Literal["ParquetReader"] = "ParquetReader"

    path: str

    @T.override
    def read(self) -> pd.DataFrame:
        return pd.read_parquet(self.path).head(self.limit)


ReaderKind = ParquetReader

# %% WRITERS


class Writer(abc.ABC, pdt.BaseModel, strict=True):
    """Base class for a dataset writer.

    Use a writer to save a dataset from memory.
    e.g., to write file, database, cloud storage, ...
    """

    KIND: str

    @abc.abstractmethod
    def write(self, data: pd.DataFrame) -> None:
        """Write a dataframe to a dataset.

        Args:
            data (pd.DataFrame): dataframe representation.
        """


class ParquetWriter(Writer):
    """Writer a dataframe to a parquet file.

    Attributes:
        path: local or remote file to a dataset.
    """

    KIND: T.Literal["ParquetWriter"] = "ParquetWriter"

    path: str

    @T.override
    def write(self, data: pd.DataFrame) -> None:
        pd.DataFrame.to_parquet(data, self.path)


WriterKind = ParquetWriter
