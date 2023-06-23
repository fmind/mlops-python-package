"""Define and validate dataframe schemas."""

# %% IMPORTS

import pandas as pd
import pandera as pa
import pandera.typing as papd

# %% SCHEMAS


class Schema(pa.SchemaModel):
    """Base class for a schema."""

    # note: use schemas to type your dataframes
    # e.g., to communicate and validate its fields

    class Config:
        """Default configuration."""

        coerce = True
        strict = True

    @classmethod  # no typing to ease the integration
    def check(cls, data: pd.DataFrame, **kwargs):
        """Check the data with this schema."""
        return cls.validate(data, **kwargs)


class InputsSchema(Schema):
    """Schema for the project inputs."""

    alcohol: papd.Series[float] = pa.Field(gt=0, lt=100)
    malic_acid: papd.Series[float] = pa.Field(gt=0, lt=10)
    ash: papd.Series[float] = pa.Field(gt=0, lt=10)
    alcalinity_of_ash: papd.Series[float] = pa.Field(gt=0, lt=100)
    magnesium: papd.Series[float] = pa.Field(gt=0, lt=1000)
    total_phenols: papd.Series[float] = pa.Field(gt=0, lt=10)
    flavanoids: papd.Series[float] = pa.Field(gt=0, lt=10)
    nonflavanoid_phenols: papd.Series[float] = pa.Field(gt=0, lt=10)
    proanthocyanins: papd.Series[float] = pa.Field(gt=0, lt=10)
    color_intensity: papd.Series[float] = pa.Field(gt=0, lt=100)
    hue: papd.Series[float] = pa.Field(gt=0, lt=10)
    od280_od315_of_diluted_wines: papd.Series[float] = pa.Field(gt=0, lt=10)
    proline: papd.Series[float] = pa.Field(gt=0, lt=10000)


# alias types for inputs schema
Inputs = papd.DataFrame[InputsSchema]


class TargetSchema(Schema):
    """Schema for the project target."""

    target: papd.Series[int] = pa.Field(isin=[0, 1, 2])


# alias types for target schema
Target = papd.DataFrame[TargetSchema]


class OutputSchema(Schema):
    """Schema for the project output."""

    output: papd.Series[int] = pa.Field(isin=[0, 1, 2])


# alias types for output schema
Output = papd.DataFrame[OutputSchema]
