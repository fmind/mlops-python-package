"""Define and validate dataframe schemas."""

# %% IMPORTS

import typing as T

import pandera.polars as pa
import pandera.typing.polars as pat
import polars as pl

# %% TYPES

# Generic type for a dataframe container
TSchema = T.TypeVar("TSchema", bound="pa.DataFrameModel")

# %% SCHEMAS


class Schema(pa.DataFrameModel):
    """Base class for a dataframe schema.

    Use a schema to type your dataframe object.
    e.g., to communicate and validate its fields.
    """

    class Config:
        """Default configurations for all schemas.

        Parameters:
            coerce (bool): convert data type if possible.
            strict (bool): ensure the data type is correct.
        """

        coerce: bool = True
        strict: bool = True

    @classmethod
    def check(cls: T.Type[TSchema], data: pl.DataFrame) -> pat.DataFrame[TSchema]:
        """Check the dataframe with this schema.

        Args:
            data (pl.DataFrame): dataframe to check.

        Returns:
            pat.DataFrame[TSchema]: validated dataframe.
        """
        return T.cast(pat.DataFrame[TSchema], cls.validate(data))


class InputsSchema(Schema):
    """Schema for the project inputs."""

    instant: pl.UInt32 = pa.Field(ge=0)
    dteday: pl.Datetime = pa.Field()
    season: pl.UInt8 = pa.Field(isin=[1, 2, 3, 4])
    yr: pl.UInt8 = pa.Field(ge=0, le=1)
    mnth: pl.UInt8 = pa.Field(ge=1, le=12)
    hr: pl.UInt8 = pa.Field(ge=0, le=23)
    holiday: pl.Boolean = pa.Field()
    weekday: pl.UInt8 = pa.Field(ge=0, le=6)
    workingday: pl.Boolean = pa.Field()
    weathersit: pl.UInt8 = pa.Field(ge=1, le=4)
    temp: pl.Float32 = pa.Field(ge=0, le=1)
    atemp: pl.Float32 = pa.Field(ge=0, le=1)
    hum: pl.Float32 = pa.Field(ge=0, le=1)
    windspeed: pl.Float32 = pa.Field(ge=0, le=1)
    casual: pl.UInt32 = pa.Field(ge=0)
    registered: pl.UInt32 = pa.Field(ge=0)


Inputs = pat.DataFrame[InputsSchema]


class TargetsSchema(Schema):
    """Schema for the project target."""

    cnt: pl.UInt32 = pa.Field(ge=0)


Targets = pat.DataFrame[TargetsSchema]


class OutputsSchema(Schema):
    """Schema for the project output."""

    prediction: pl.UInt32 = pa.Field(ge=0)


Outputs = pat.DataFrame[OutputsSchema]


class SHAPValuesSchema(Schema):
    """Schema for the project shap values."""

    class Config:
        """Default configurations this schema.

        Parameters:
            dtype (str): dataframe default data type.
            strict (bool): ensure the data type is correct.
        """

        dtype: str = "float32"
        strict: bool = False


SHAPValues = pat.DataFrame[SHAPValuesSchema]


class FeatureImportancesSchema(Schema):
    """Schema for the project feature importances."""

    feature: pl.String = pa.Field()
    importance: pl.Float32 = pa.Field()


FeatureImportances = pat.DataFrame[FeatureImportancesSchema]
