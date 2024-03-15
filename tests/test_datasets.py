# %% IMPORTS

import os

import pytest
from bikes import datasets, schemas

# %% READERS


@pytest.mark.parametrize("limit", [None, 50])
def test_parquet_reader(limit: int | None, inputs_path: str) -> None:
    # given
    reader = datasets.ParquetReader(path=inputs_path, limit=limit)
    # when
    data = reader.read()
    # then
    assert data.ndim == 2, "Data should be a dataframe!"
    if limit is not None:
        assert len(data) == limit, "Data should have the limit size!"


# %% WRITERS


def test_parquet_writer(targets: schemas.Targets, tmp_outputs_path: str) -> None:
    # given
    writer = datasets.ParquetWriter(path=tmp_outputs_path)
    # when
    writer.write(data=targets)
    # then
    assert os.path.exists(tmp_outputs_path), "Data should be written!"
