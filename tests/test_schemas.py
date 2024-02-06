"""Test the schemas module."""

# pylint: disable=missing-docstring

# %% IMPORTS

from bikes import datasets, schemas

# %% SCHEMAS


def test_inputs_schema(tests_inputs_reader: datasets.ParquetReader):
    # given
    schema = schemas.InputsSchema
    # when
    data = tests_inputs_reader.read()
    # then
    assert schema.check(data) is not None, "Inputs data should be valid!"


def test_targets_schema(tests_targets_reader: datasets.ParquetReader):
    # given
    schema = schemas.TargetsSchema
    # when
    data = tests_targets_reader.read()
    # then
    assert schema.check(data) is not None, "Targets data should be valid!"


def test_output_schema(tests_outputs_reader: datasets.ParquetReader):
    # given
    schema = schemas.OutputsSchema
    # when
    data = tests_outputs_reader.read()
    # then
    assert schema.check(data) is not None, "Outputs data should be valid!"
