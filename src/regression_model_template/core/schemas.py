"""Define and validate dataframe schemas."""

# %% IMPORTS

import typing as T

import pandas as pd
import pandera as pa
import pandera.typing as papd
import pandera.typing.common as padt

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
    def check(cls: T.Type[TSchema], data: pd.DataFrame) -> papd.DataFrame[TSchema]:
        """Check the dataframe with this schema.

        Args:
            data (pd.DataFrame): dataframe to check.

        Returns:
            papd.DataFrame[TSchema]: validated dataframe.
        """
        return T.cast(papd.DataFrame[TSchema], cls.validate(data))


class InputsSchema(Schema):
    """Schema for the project inputs."""

    instant: papd.Index[padt.UInt32] = pa.Field(ge=0)
    dteday: papd.Series[padt.DateTime] = pa.Field()
    season: papd.Series[padt.UInt8] = pa.Field(isin=[1, 2, 3, 4])
    yr: papd.Series[padt.UInt8] = pa.Field(ge=0, le=1)
    mnth: papd.Series[padt.UInt8] = pa.Field(ge=1, le=12)
    hr: papd.Series[padt.UInt8] = pa.Field(ge=0, le=23)
    holiday: papd.Series[padt.Bool] = pa.Field()
    weekday: papd.Series[padt.UInt8] = pa.Field(ge=0, le=6)
    workingday: papd.Series[padt.Bool] = pa.Field()
    weathersit: papd.Series[padt.UInt8] = pa.Field(ge=1, le=4)
    temp: papd.Series[padt.Float16] = pa.Field(ge=0, le=1)
    atemp: papd.Series[padt.Float16] = pa.Field(ge=0, le=1)
    hum: papd.Series[padt.Float16] = pa.Field(ge=0, le=1)
    windspeed: papd.Series[padt.Float16] = pa.Field(ge=0, le=1)
    casual: papd.Series[padt.UInt32] = pa.Field(ge=0)
    registered: papd.Series[padt.UInt32] = pa.Field(ge=0)


Inputs = papd.DataFrame[InputsSchema]


class TargetsSchema(Schema):
    """Schema for the project target."""

    instant: papd.Index[padt.UInt32] = pa.Field(ge=0)
    cnt: papd.Series[padt.UInt32] = pa.Field(ge=0)


Targets = papd.DataFrame[TargetsSchema]


class OutputsSchema(Schema):
    """Schema for the project output."""

    instant: papd.Index[padt.UInt32] = pa.Field(ge=0)
    prediction: papd.Series[padt.UInt32] = pa.Field(ge=0)


Outputs = papd.DataFrame[OutputsSchema]


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


SHAPValues = papd.DataFrame[SHAPValuesSchema]


class FeatureImportancesSchema(Schema):
    """Schema for the project feature importances."""

    feature: papd.Series[padt.String] = pa.Field()
    importance: papd.Series[padt.Float32] = pa.Field()


FeatureImportances = papd.DataFrame[FeatureImportancesSchema]
