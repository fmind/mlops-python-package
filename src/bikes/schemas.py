"""Define and validate dataframe schemas."""

# %% IMPORTS

import pandas as pd
import pandera as pa
import pandera.typing as papd

# %% SCHEMAS


class Schema(pa.DataFrameModel):
    """Base class for a dataframe schema.

    Use a schema to type your dataframe object.
    e.g., to communicate and validate its fields.
    """

    class Config:
        """Default configuration.

        Attributes:
            coerce: convert data type if possible.
            strict: ensure the data type is correct.
        """

        coerce = True
        strict = True

    @classmethod
    def check(cls, data: pd.DataFrame, **kwargs):
        """Check the data with this schema.

        Args:
            data (pd.DataFrame): dataframe to check.

        Returns:
            _type_: validated dataframe with schema.
        """
        return cls.validate(data, **kwargs)


class InputsSchema(Schema):
    """Schema for the project inputs."""

    instant: papd.Index[papd.UInt32] = pa.Field(ge=0, check_name=True)
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
    casual: papd.Series[papd.UInt32] = pa.Field(ge=0)
    registered: papd.Series[papd.UInt32] = pa.Field(ge=0)


Inputs = papd.DataFrame[InputsSchema]


class TargetsSchema(Schema):
    """Schema for the project target."""

    instant: papd.Index[papd.UInt32] = pa.Field(ge=0, check_name=True)
    cnt: papd.Series[papd.UInt32] = pa.Field(ge=0)


Targets = papd.DataFrame[TargetsSchema]


class OutputsSchema(Schema):
    """Schema for the project output."""

    instant: papd.Index[papd.UInt32] = pa.Field(ge=0, check_name=True)
    prediction: papd.Series[papd.UInt32] = pa.Field(ge=0)


Outputs = papd.DataFrame[OutputsSchema]
