# %% IMPORTS

import pandas as pd
import pandera.errors as pe
import pytest

from bikes.core import models, schemas
from bikes.io import datasets

# %% SCHEMAS


def test_inputs_schema(inputs_reader: datasets.Reader) -> None:
    # given
    schema = schemas.InputsSchema
    # when
    data = inputs_reader.read()
    # then
    assert schema.check(data) is not None, "Inputs data should be valid!"


def test_targets_schema(targets_reader: datasets.Reader) -> None:
    # given
    schema = schemas.TargetsSchema
    # when
    data = targets_reader.read()
    # then
    assert schema.check(data) is not None, "Targets data should be valid!"


def test_outputs_schema(outputs_reader: datasets.Reader) -> None:
    # given
    schema = schemas.OutputsSchema
    # when
    data = outputs_reader.read()
    # then
    assert schema.check(data) is not None, "Outputs data should be valid!"


def test_shap_values_schema(
    model: models.Model,
    train_test_sets: tuple[schemas.Inputs, schemas.Targets, schemas.Inputs, schemas.Targets],
) -> None:
    # given
    schema = schemas.SHAPValuesSchema
    _, _, inputs_test, _ = train_test_sets
    # when
    data = model.explain_samples(inputs=inputs_test)
    # then
    assert schema.check(data) is not None, "SHAP values data should be valid!"


def test_feature_importances_schema(model: models.Model) -> None:
    # given
    schema = schemas.FeatureImportancesSchema
    # when
    data = model.explain_model()
    # then
    assert schema.check(data) is not None, "Feature importance data should be valid!"


@pytest.mark.parametrize(("column", "value"), [("hr", 256.5), ("hr", 1.5), ("holiday", 2), ("holiday", "False")])
def test_inputs_reject_lossy_coercion(inputs: schemas.Inputs, column: str, value: float | str) -> None:
    invalid = inputs.copy()
    invalid[column] = value
    with pytest.raises((TypeError, ValueError, OverflowError)):
        schemas.InputsSchema.check(invalid)


@pytest.mark.parametrize("value", [1.5, 4294967296.5, -1.0])
def test_targets_reject_lossy_counts(targets: schemas.Targets, value: float) -> None:
    invalid = targets.copy()
    invalid["cnt"] = value
    with pytest.raises((TypeError, ValueError, OverflowError)):
        schemas.TargetsSchema.check(invalid)


def test_inputs_accept_lossless_csv_values(inputs: schemas.Inputs) -> None:
    raw = inputs.copy()
    raw["hr"] = raw["hr"].astype(str)
    raw["yr"] = raw["yr"].astype(float)
    raw["holiday"] = raw["holiday"].astype(int)
    checked = schemas.InputsSchema.check(raw)
    pd.testing.assert_frame_equal(checked, inputs)


@pytest.mark.parametrize("index", [[1.5, 2.0], [4294967296.0, 2.0]])
def test_targets_reject_lossy_ids(targets: schemas.Targets, index: list[float]) -> None:
    invalid = targets.iloc[:2].copy()
    invalid.index = pd.Index(index, name="instant")
    with pytest.raises((TypeError, ValueError, OverflowError)):
        schemas.TargetsSchema.check(invalid)


def test_targets_reject_duplicate_ids(targets: schemas.Targets) -> None:
    invalid = targets.iloc[:2].copy()
    invalid.index = pd.Index([1, 1], name="instant")
    with pytest.raises(pe.SchemaError, match="duplicate values"):
        schemas.TargetsSchema.check(invalid)


def test_serving_inputs_exclude_target_derived_counts(inputs: schemas.Inputs) -> None:
    assert {"casual", "registered"}.isdisjoint(inputs.columns)
    assert schemas.InputsSchema.check(inputs) is not None
    invalid = inputs.copy()
    invalid["casual"] = 0
    with pytest.raises((pe.SchemaError, pe.SchemaErrors), match="not in DataFrameSchema"):
        schemas.InputsSchema.check(invalid)
