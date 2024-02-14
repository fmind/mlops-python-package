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
    """Base class for a model serializer.

    Use serializer to save the model objects.
    e.g., to export the model to a pickle file.
    """

    KIND: str

    @abc.abstractmethod
    def save(self, model: models.Model) -> None:
        """Save the model to a given destination.

        Args:
            model (models.Model): model to save.
        """


class JoblibModelSerializer(ModelSerializer):
    """Model serializer based on joblib.

    Attributes:
        path: output path for the model.
    """

    KIND: T.Literal["JoblibModelSerializer"] = "JoblibModelSerializer"

    path: str

    @T.override
    def save(self, model: models.Model) -> None:
        jl.dump(model, self.path)


ModelSerializerKind = JoblibModelSerializer


# %% - Deserializers


class ModelDeserializer(abc.ABC, pdt.BaseModel, strict=True):
    """Base class for a model deserializer.

    Use deserializer to load the model objects.
    e.g., to import the model from a pickle file.
    """

    KIND: str

    @abc.abstractmethod
    def load(self) -> models.Model:
        """Load the model from a given source.

        Returns:
            models.Model: loaded model.
        """


class JoblibModelDeserializer(ModelDeserializer):
    """Model deserializer based on joblib.

    Attributes:
        path: source path for the model.
    """

    KIND: T.Literal["JoblibModelDeserializer"] = "JoblibModelDeserializer"

    path: str

    @T.override
    def load(self) -> models.Model:
        return jl.load(self.path)


ModelDeserializerKind = JoblibModelDeserializer
