"""Adapters, signers, savers, and loaders for model registries."""

# %% IMPORTS

import abc
import typing as T

import mlflow
import pydantic as pdt

from bikes import models, schemas

# %% TYPES

Info: T.TypeAlias = mlflow.models.model.ModelInfo
Version: T.TypeAlias = mlflow.entities.model_registry.ModelVersion
Signature: T.TypeAlias = mlflow.models.ModelSignature
CustomModel: T.TypeAlias = mlflow.pyfunc.PythonModel

# %% ADAPTERS


class CustomAdapter(mlflow.pyfunc.PythonModel):
    """Adapt a custom model to the MLflow PyFunc flavor.

    https://mlflow.org/docs/latest/python_api/mlflow.pyfunc.html
    """

    def __init__(self, model: models.Model):
        """Initialize the custom adapter.

        Args:
            model (models.Model): project model.
        """
        self.model = model

    def predict(
        self, context: mlflow.pyfunc.PythonModelContext, inputs: schemas.Inputs
    ) -> schemas.Outputs:
        """Generate predictions from a custom model.

        Args:
            context (mlflow.pyfunc.PythonModelContext): ignored.
            inputs (schemas.Inputs): inputs for the model.

        Returns:
            schemas.Outputs: outputs of the model.
        """
        return self.model.predict(inputs=inputs)


# %% SIGNERS


class Signer(abc.ABC, pdt.BaseModel, strict=True):
    """Base class for making signatures.

    Allow to switch between signing approaches.
    e.g., automatic inference vs manual signatures
    https://mlflow.org/docs/latest/models.html#model-signature-and-input-example
    """

    KIND: str

    @abc.abstractmethod
    def sign(self, inputs: schemas.Inputs, outputs: schemas.Outputs) -> Signature:
        """Make a model signature from inputs/outputs.

        Args:
            inputs (schemas.Inputs): inputs of the model.
            outputs (schemas.Outputs): ouputs of the model.

        Returns:
            ModelSignature: generated signature for the model.
        """


class InferSigner(Signer):
    """Generate model signatures from data inference."""

    KIND: T.Literal["InferModelSigner"] = "InferModelSigner"

    @T.override
    def sign(self, inputs: schemas.Inputs, outputs: schemas.Outputs) -> Signature:
        return mlflow.models.infer_signature(model_input=inputs, model_output=outputs)


SignerKind = InferSigner


# %% SAVERS


class Saver(abc.ABC, pdt.BaseModel, strict=True):
    """Base class for saving models in registry.

    Separate model definition from serialization.
    e.g., to switch between serialization flavors.

    Attributes:
        path (str): model path inside the MLflow artifact store.
    """

    KIND: str

    path: str = "model"

    @abc.abstractmethod
    def save(
        self, model: models.Model, signature: Signature, input_example: schemas.Inputs
    ) -> Info:
        """Save a model in the model registry.

        Args:
            model (models.Model): model to save.
            signature (Signature): model signature.
            input_example (schemas.Inputs): inputs sample.

        Returns:
            Info: model saving information.
        """


class CustomSaver(Saver):
    """Saver for custom models using the MLflow PyFunc module.

    https://mlflow.org/docs/latest/python_api/mlflow.pyfunc.html
    """

    KIND: T.Literal["CustomSaver"] = "CustomSaver"

    def save(
        self, model: models.Model, signature: Signature, input_example: schemas.Inputs
    ) -> Info:
        """Save a custom model to the MLflow Model Registry."""
        custom = CustomAdapter(model=model)  # adapt model
        return mlflow.pyfunc.log_model(
            artifact_path=self.path,
            python_model=custom,
            signature=signature,
            input_example=input_example,
        )


SaverKind = CustomSaver


# %% LOADERS


class Loader(abc.ABC, pdt.BaseModel, strict=True):
    """Base class for loading models from registry.

    Separate model definition from deserialization.
    e.g., to switch between deserialization flavors.
    """

    KIND: str

    @abc.abstractmethod
    def load(self, uri: str) -> T.Any:
        """Load a model from the model registry.

        Args:
            uri (str): URI of the model to load.

        Returns:
            T.Any: model loaded from registry.
        """


class CustomLoader(Loader):
    """Loader for custom models using the MLflow PyFunc module.

    https://mlflow.org/docs/latest/python_api/mlflow.pyfunc.html
    """

    KIND: T.Literal["CustomLoader"] = "CustomLoader"

    @T.override
    def load(self, uri: str) -> CustomModel:
        return mlflow.pyfunc.load_model(model_uri=uri)


LoaderKind = CustomLoader
