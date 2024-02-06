"""Define machine learning models for the project."""

# %% IMPORTS

import abc
import typing as T

import pydantic as pdt
from sklearn import compose, ensemble, pipeline, preprocessing

from bikes import schemas

# %% TYPES

ParamKey = str
ParamValue = T.Any
Params = dict[ParamKey, ParamValue]

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
        for key, value in self.model_dump().items():
            if not key.startswith("_") and not key.isupper():
                params[key] = value
        return params

    def set_params(self, **params: ParamValue) -> "Model":
        """Set the model params in place."""
        for key, value in params.items():
            setattr(self, key, value)
        return self

    @abc.abstractmethod
    def fit(self, inputs: schemas.Inputs, targets: schemas.Targets) -> "Model":
        """Fit the model on the given inputs and targets."""

    @abc.abstractmethod
    def predict(self, inputs: schemas.Inputs) -> schemas.Outputs:
        """Generate outputs with the model for the given inputs."""


class BaselineSklearnModel(Model):
    """Simple baseline model built on top of sklearn."""

    KIND: T.Literal["BaselineSklearnModel"] = "BaselineSklearnModel"

    # params
    max_depth: int = 20
    n_estimators: int = 299
    random_state: int | None = 42
    # private
    _pipeline: pipeline.Pipeline | None = None
    _numericals: list[str] = [
        "yr",
        "mnth",
        "hr",
        "holiday",
        "weekday",
        "workingday",
        "temp",
        "atemp",
        "hum",
        "windspeed",
        "casual",
        # "registered", # too correlated with target
    ]
    _categoricals: list[str] = [
        "season",
        "weathersit",
    ]

    def fit(self, inputs: schemas.Inputs, targets: schemas.Targets) -> "BaselineSklearnModel":
        """Fit the baseline sklearn model on the given inputs and targets."""
        categoricals_transformer = preprocessing.OneHotEncoder(sparse_output=False, handle_unknown="ignore")
        transformer = compose.ColumnTransformer(
            [
                ("categoricals", categoricals_transformer, self._categoricals),
                ("numericals", "passthrough", self._numericals),
            ],
            remainder="drop",
        )
        regressor = ensemble.RandomForestRegressor(
            max_depth=self.max_depth, n_estimators=self.n_estimators, random_state=self.random_state
        )
        self._pipeline = pipeline.Pipeline(
            steps=[
                ("transformer", transformer),
                ("regressor", regressor),
            ]
        )
        self._pipeline.fit(X=inputs, y=targets[schemas.TargetsSchema.cnt])
        return self

    def predict(self, inputs: schemas.Inputs) -> schemas.Outputs:
        """Generate outputs with the baseline sklearn model for the given inputs."""
        assert self._pipeline is not None, "Model should be fitted first!"
        prediction = self._pipeline.predict(inputs)  # return an np.ndarray not a dataframe!
        outputs = schemas.Outputs({schemas.OutputsSchema.prediction: prediction}, index=inputs.index)
        return outputs


ModelKind = BaselineSklearnModel
