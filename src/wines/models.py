"""Define adaptable machine learning models."""

# %% IMPORTS

import abc
import typing as T

import joblib as jl
import pydantic as pdt
from sklearn import ensemble, pipeline

from wines import schemas

# %% TYPINGS

ParamKey = str
ParamValue = T.Any
Params = T.Dict[ParamKey, ParamValue]

# %% MODELS


class Model(abc.ABC, pdt.BaseModel):
    """Base class for a model."""

    # note: use models to adapt AI/ML frameworks
    # e.g., to swap easily one model with another

    class Config:
        """Default pydantic config."""

        underscore_attrs_are_private = True

    KIND: str

    # pylint: disable=unused-argument
    def get_params(self, deep: bool = True) -> Params:
        """Get the model params."""
        params: Params = {}
        for key, value in self.dict().items():
            if not key.startswith("_") and not key.isupper():
                params[key] = value
        return params

    def set_params(self, **params: ParamValue) -> "Model":
        """Set the model params in place."""
        for key, value in params.items():
            setattr(self, key, value)
        return self

    @abc.abstractmethod
    def fit(self, inputs: schemas.Inputs, target: schemas.Target) -> "Model":
        """Fit the model on the given inputs and target."""

    @abc.abstractmethod
    def predict(self, inputs: schemas.Inputs) -> schemas.Output:
        """Generate an output with the model for the given inputs."""

    def save(self, path: str) -> None:
        """Save the model to the given path."""
        jl.dump(self, path)

    @classmethod
    def load(cls, path: str) -> "Model":
        """Load the model from the given path."""
        return jl.load(path)


class BaselineSklearnModel(Model):
    """Simple model based on sklearn."""

    KIND: T.Literal["BaselineSklearnModel"] = "BaselineSklearnModel"

    # params
    max_depth: int = 5
    n_estimators: int = 20
    random_state: int | None = 42
    # private
    _pipeline: T.Optional[pipeline.Pipeline] = None

    def fit(self, inputs: schemas.Inputs, target: schemas.Target) -> "BaselineSklearnModel":
        """Fit the baseline sklearn model on the given inputs and target."""
        classifier = ensemble.RandomForestClassifier(
            max_depth=self.max_depth,
            n_estimators=self.n_estimators,
            random_state=self.random_state,
        )
        self._pipeline = pipeline.Pipeline([("classifier", classifier)])
        self._pipeline.fit(X=inputs, y=target["target"])
        return self

    def predict(self, inputs: schemas.Inputs) -> schemas.Output:
        """Generate an output with the baseline sklearn model for the given inputs."""
        assert self._pipeline is not None, "Model should be fitted first!"
        predictions = self._pipeline.predict(inputs)  # np.ndarray
        output = schemas.Output({"output": predictions})
        return output


# alias to all model kinds
# note: convert to Union with 2+ types
ModelKind = BaselineSklearnModel
