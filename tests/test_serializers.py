"""Test the serializers module."""

# pylint: disable=missing-docstring

# %% IMPORTS

import os

from bikes import models, serializers

# %% MODELS


def test_joblib_model_serializer_deserializer(empty_model: models.Model, tmp_model_path: str):
    # given
    serializer = serializers.JoblibModelSerializer(path=tmp_model_path)
    deserializer = serializers.JoblibModelDeserializer(path=tmp_model_path)
    # when
    serializer.save(model=empty_model)
    model = deserializer.load()
    # then
    assert os.path.exists(tmp_model_path), "Model should be saved to the given path!"
    assert model.get_params() == empty_model.get_params(), "Model and deserialized model should be the same!"
