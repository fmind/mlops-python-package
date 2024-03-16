# %% IMPORTS

from bikes.core import schemas
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
