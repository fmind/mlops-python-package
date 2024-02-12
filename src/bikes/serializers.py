"""Define objects serializers and deserializers."""

# %% IMPORTS

import abc
import typing as T

import joblib as jl
import pydantic as pdt

from bikes import models

# %% MODELS

# %% - Serializers


class ModelSerializer(abc.ABC, pdt.BaseModel, strict=True):
    """Base class for a model serializer."""

    # note: use serializer to save model objects
    # e.g., to export the model to a pickle file

    KIND: str

    @abc.abstractmethod
    def save(self, model: models.Model) -> None:
        """Save the model to a given destination."""


class JoblibModelSerializer(ModelSerializer):
    """Model serializer based on joblib."""

    KIND: T.Literal["JoblibModelSerializer"] = "JoblibModelSerializer"

    path: str

    def save(self, model: models.Model) -> None:
        """Save the model to the given path."""
        jl.dump(model, self.path)


ModelSerializerKind = JoblibModelSerializer


# %% - Deserializers


class ModelDeserializer(abc.ABC, pdt.BaseModel, strict=True):
    """Base class for a model deserializer."""

    # note: use serializer to load model objects
    # e.g., to import the model from a pickle file

    KIND: str

    @abc.abstractmethod
    def load(self) -> models.Model:
        """Load the model from a given source."""


class JoblibModelDeserializer(ModelDeserializer):
    """Model deserializer based on joblib."""

    KIND: T.Literal["JoblibModelDeserializer"] = "JoblibModelDeserializer"

    path: str

    def load(self) -> models.Model:
        """Load the model from the given path."""
        return jl.load(self.path)


ModelDeserializerKind = JoblibModelDeserializer
