"""Define and validate dataframe schemas."""

# %% IMPORTS

import typing as T

import pandas as pd
import pandera.pandas as pa
import pandera.typing.pandas as papd
from pandera.api.pandas.model_config import BaseConfig

# %% TYPES

# Generic type for a dataframe container
TSchema = T.TypeVar("TSchema", bound="pa.DataFrameModel")

# %% SCHEMAS


class SchemaConfig(BaseConfig):
    """Default configurations for all schemas.

    Parameters:
        coerce (bool): convert data type if possible.
        strict (bool): ensure the data type is correct.
    """

    coerce: bool = True
    strict: bool = True


class Schema(pa.DataFrameModel):
    """Base class for a dataframe schema.

    Use a schema to type your dataframe object.
    e.g., to communicate and validate its fields.
    """

    Config: type[SchemaConfig] = SchemaConfig

    @classmethod
    def check(cls: type[TSchema], data: pd.DataFrame) -> papd.DataFrame[TSchema]:
        """Check the dataframe with this schema.

        Args:
            data (pd.DataFrame): dataframe to check.

        Returns:
            papd.DataFrame[TSchema]: validated dataframe.
        """
        return cls.validate(data)

    # Pandas' nullable casts reject truncation and overflow before Pandera narrows
    # to the public NumPy dtypes. NumPy astype alone can turn hr=256.5 into zero.
    @pa.parser(r"^(season|yr|mnth|hr|weekday|weathersit)$", regex=True)
    @classmethod
    def parse_uint8(cls, data: pd.Series) -> pd.Series:
        """Check that small integer fields can be converted without data loss."""
        return data.astype("UInt8")

    @pa.parser(r"^(instant|cnt|prediction)$", regex=True)
    @classmethod
    def parse_uint32(cls, data: pd.Series) -> pd.Series:
        """Check that sample IDs and counts can be converted without data loss."""
        return data.astype("UInt32")

    @pa.parser(r"^(holiday|workingday)$", regex=True)
    @classmethod
    def parse_boolean(cls, data: pd.Series) -> pd.Series:
        """Accept booleans and zero/one values without truthiness coercion."""
        return data.astype("boolean")


class InputsSchema(Schema):
    """Shared training and serving inputs, excluding target-derived rental counts."""

    instant: papd.Index[papd.UInt32] = pa.Field(ge=0, unique=True)
    dteday: papd.Series[papd.DateTime] = pa.Field()
    season: papd.Series[papd.UInt8] = pa.Field(isin=[1, 2, 3, 4])
    yr: papd.Series[papd.UInt8] = pa.Field(ge=0, le=1)
    mnth: papd.Series[papd.UInt8] = pa.Field(ge=1, le=12)
    hr: papd.Series[papd.UInt8] = pa.Field(ge=0, le=23)
    holiday: papd.Series[papd.Bool] = pa.Field()
    weekday: papd.Series[papd.UInt8] = pa.Field(ge=0, le=6)
    workingday: papd.Series[papd.Bool] = pa.Field()
    weathersit: papd.Series[papd.UInt8] = pa.Field(ge=1, le=4)
    temp: papd.Series[papd.Float16] = pa.Field(ge=0, le=1)
    atemp: papd.Series[papd.Float16] = pa.Field(ge=0, le=1)
    hum: papd.Series[papd.Float16] = pa.Field(ge=0, le=1)
    windspeed: papd.Series[papd.Float16] = pa.Field(ge=0, le=1)


Inputs = papd.DataFrame[InputsSchema]


class TargetsSchema(Schema):
    """Schema for the project target."""

    instant: papd.Index[papd.UInt32] = pa.Field(ge=0, unique=True)
    cnt: papd.Series[papd.UInt32] = pa.Field(ge=0)


Targets = papd.DataFrame[TargetsSchema]


class OutputsSchema(Schema):
    """Schema for the project output."""

    instant: papd.Index[papd.UInt32] = pa.Field(ge=0, unique=True)
    prediction: papd.Series[papd.UInt32] = pa.Field(ge=0)


Outputs = papd.DataFrame[OutputsSchema]


class SHAPValuesConfig(SchemaConfig):
    """Default configurations this schema.

    Parameters:
        dtype (str): dataframe default data type.
        strict (bool): ensure the data type is correct.
    """

    dtype: str = "float32"
    strict: bool = False


class SHAPValuesSchema(Schema):
    """Schema for the project shap values."""

    Config: type[SHAPValuesConfig] = SHAPValuesConfig


SHAPValues = papd.DataFrame[SHAPValuesSchema]


class FeatureImportancesSchema(Schema):
    """Schema for the project feature importances."""

    feature: papd.Series[papd.String] = pa.Field()
    importance: papd.Series[papd.Float32] = pa.Field()


FeatureImportances = papd.DataFrame[FeatureImportancesSchema]
