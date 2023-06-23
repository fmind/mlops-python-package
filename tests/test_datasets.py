"""Test the datasets module."""
# pylint: disable=missing-docstring

# %% IMPORTS

import os

from wines import datasets

# %% DATASETS


def test_parquet_dataset(inputs_path: str, tmp_output_path: str):
    # given
    source = datasets.ParquetDataset(path=inputs_path)
    dest = datasets.ParquetDataset(path=tmp_output_path)
    # when
    data = source.read()
    dest.write(data)
    # then
    assert data.ndim == 2, "Data should be 2-dim dataframe!"
    assert os.path.exists(tmp_output_path), "Output file should exist!"
