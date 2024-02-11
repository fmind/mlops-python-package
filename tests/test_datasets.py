"""Test the datasets module."""

# pylint: disable=missing-docstring

# %% IMPORTS

import os

from bikes import datasets, schemas

# %% DATASETS


def test_parquet_reader(inputs_path: str):
    # given
    limit = 50
    reader = datasets.ParquetReader(path=inputs_path, limit=limit)
    # when
    data = reader.read()
    # then
    assert data.ndim == 2, "Data should be a dataframe!"
    assert len(data) == limit, "Data should have the limit size!"


def test_parquet_writer(targets: schemas.Targets, tmp_outputs_path: str):
    # given
    writer = datasets.ParquetWriter(path=tmp_outputs_path)
    # when
    writer.write(data=targets)
    # then
    assert os.path.exists(tmp_outputs_path), "Data should be written!"
