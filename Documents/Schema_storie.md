# US [Scchemas](./backlog_mlops_regresion.md) : Define structured data formats for input, output, and intermediate processes, ensuring consistency and validation throughout the pipeline.

- [Uml diagram of the package](#uml-diagram-of-the-package)
- [Code location](#code-location)
- [Test location](#test-location)

------------

## Uml diagram of the package

```plantuml
@startuml classes_Models
set namespaceSeparator none
class "Config" as model_name.core.schemas.Schema.Config {
  coerce : bool
  strict : bool
}
class "Config" as model_name.core.schemas.SHAPValuesSchema.Config {
  dtype : str
  strict : bool
}
class "FeatureImportancesSchema" as model_name.core.schemas.FeatureImportancesSchema {
  feature : papd.Series[padt.String]
  importance : papd.Series[padt.Float32]
}
class "InputsSchema" as model_name.core.schemas.InputsSchema {
  atemp : papd.Series[padt.Float16]
  casual : papd.Series[padt.UInt32]
  dteday : papd.Series[padt.DateTime]
  holiday : papd.Series[padt.Bool]
  hr : papd.Series[padt.UInt8]
  hum : papd.Series[padt.Float16]
  instant : papd.Index[padt.UInt32]
  mnth : papd.Series[padt.UInt8]
  registered : papd.Series[padt.UInt32]
  season : papd.Series[padt.UInt8]
  temp : papd.Series[padt.Float16]
  weathersit : papd.Series[padt.UInt8]
  weekday : papd.Series[padt.UInt8]
  windspeed : papd.Series[padt.Float16]
  workingday : papd.Series[padt.Bool]
  yr : papd.Series[padt.UInt8]
}
class "OutputsSchema" as model_name.core.schemas.OutputsSchema {
  instant : papd.Index[padt.UInt32]
  prediction : papd.Series[padt.UInt32]
}
class "SHAPValuesSchema" as model_name.core.schemas.SHAPValuesSchema {
}
class "Schema" as model_name.core.schemas.Schema {
  check(data: pd.DataFrame) -> papd.DataFrame[TSchema]
}
class "TargetsSchema" as model_name.core.schemas.TargetsSchema {
  cnt : papd.Series[padt.UInt32]
  instant : papd.Index[padt.UInt32]
}
model_name.core.schemas.FeatureImportancesSchema --|> model_name.core.schemas.Schema
model_name.core.schemas.InputsSchema --|> model_name.core.schemas.Schema
model_name.core.schemas.OutputsSchema --|> model_name.core.schemas.Schema
model_name.core.schemas.SHAPValuesSchema --|> model_name.core.schemas.Schema
model_name.core.schemas.TargetsSchema --|> model_name.core.schemas.Schema
@enduml

```

## Code location

[src/model_name/core/models.py](../src/model_name/core/schemas.py)

## Test location

[tests/core/test_models.py](../tests/core/schemas.py)