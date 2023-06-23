"""Test the schemas module."""
# pylint: disable=missing-docstring

# %% IMPORTS

from wines import datasets, schemas

# %% SCHEMAS


def test_inputs_schema(inputs_dataset: datasets.ParquetDataset):
    # given
    data = inputs_dataset.read()
    # when
    schema = schemas.InputsSchema
    # then
    assert schema.check(data) is not None, "Data should be valid!"


def test_target_schema(target_dataset: datasets.ParquetDataset):
    # given
    data = target_dataset.read()
    # when
    schema = schemas.TargetSchema
    # then
    assert schema.check(data) is not None, "Data should be valid!"


def test_output_schema(output_dataset: datasets.ParquetDataset):
    # given
    data = output_dataset.read()
    # when
    schema = schemas.OutputSchema
    # then
    assert schema.check(data) is not None, "Data should be valid!"
