"""Read/Write datasets from/to external sources/destinations."""

# %% IMPORTS

import abc
import typing as T

import mlflow.data.pandas_dataset as lineage
import pandas as pd
import pydantic as pdt

# %% TYPINGS

Lineage: T.TypeAlias = lineage.PandasDataset

# %% READERS


class Reader(abc.ABC, pdt.BaseModel, strict=True, frozen=True, extra="forbid"):
    """Base class for a dataset reader.

    Use a reader to load a dataset in memory.
    e.g., to read file, database, cloud storage, ...

    Parameters:
        limit (int, optional): maximum number of rows to read. Defaults to None.
    """

    KIND: str

    limit: int | None = None

    @abc.abstractmethod
    def read(self) -> pd.DataFrame:
        """Read a dataframe from a dataset.

        Returns:
            pd.DataFrame: dataframe representation.
        """

    @abc.abstractmethod
    def lineage(
        self,
        name: str,
        data: pd.DataFrame,
        targets: str | None = None,
        predictions: str | None = None,
    ) -> Lineage:
        """Generate lineage information.

        Args:
            name (str): dataset name.
            data (pd.DataFrame): reader dataframe.
            targets (str | None): name of the target column.
            predictions (str | None): name of the prediction column.

        Returns:
            Lineage: lineage information.
        """


class ParquetReader(Reader):
    """Read a dataframe from a parquet file.

    Parameters:
        path (str): local path to the dataset.
    """

    KIND: T.Literal["ParquetReader"] = "ParquetReader"

    path: str

    @T.override
    def read(self) -> pd.DataFrame:
        # can't limit rows at read time
        data = pd.read_parquet(self.path)
        if self.limit is not None:
            data = data.head(self.limit)
        return data

    @T.override
    def lineage(
        self,
        name: str,
        data: pd.DataFrame,
        targets: str | None = None,
        predictions: str | None = None,
    ) -> Lineage:
        return lineage.from_pandas(
            df=data, name=name, source=self.path, targets=targets, predictions=predictions
        )


ReaderKind = ParquetReader

# %% WRITERS


class Writer(abc.ABC, pdt.BaseModel, strict=True, frozen=True, extra="forbid"):
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

    Parameters:
        path (str): local or S3 path to the dataset.
    """

    KIND: T.Literal["ParquetWriter"] = "ParquetWriter"

    path: str

    @T.override
    def write(self, data: pd.DataFrame) -> None:
        pd.DataFrame.to_parquet(data, self.path)


WriterKind = ParquetWriter
