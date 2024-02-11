"""Test the serializers module."""

# pylint: disable=missing-docstring

# %% IMPORTS

import os

from bikes import models, serializers

# %% MODELS


def test_joblib_model_serializer(empty_model: models.Model, tmp_model_path: str):
    # given
    serializer = serializers.JoblibModelSerializer(path=tmp_model_path)
    # when
    serializer.save(model=empty_model)
    # then
    assert os.path.exists(tmp_model_path), "Model should be saved to the given path!"


def test_joblib_model_deserializer(default_model: models.Model, model_serializer: serializers.JoblibModelSerializer):
    # given
    model_serializer.save(model=default_model)  # save the model to a temporary path
    deserializer = serializers.JoblibModelDeserializer(path=model_serializer.path)
    # when
    model = deserializer.load()
    # then
    assert model.get_params() == default_model.get_params(), "Deserialized model should have the same params!"
