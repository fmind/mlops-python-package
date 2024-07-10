"""Define trainable machine learning models."""

# %% IMPORTS

import abc
import typing as T

import pydantic as pdt
import shap
from sklearn import compose, ensemble, pipeline, preprocessing

from bikes.core import schemas

# %% TYPES

# Model params
ParamKey = str
ParamValue = T.Any
Params = dict[ParamKey, ParamValue]

# %% MODELS


class Model(abc.ABC, pdt.BaseModel, strict=True, frozen=False, extra="forbid"):
    """Base class for a project model.

    Use a model to adapt AI/ML frameworks.
    e.g., to swap easily one model with another.
    """

    KIND: str

    def get_params(self, deep: bool = True) -> Params:
        """Get the model params.

        Args:
            deep (bool, optional): ignored.

        Returns:
            Params: internal model parameters.
        """
        params: Params = {}
        for key, value in self.model_dump().items():
            if not key.startswith("_") and not key.isupper():
                params[key] = value
        return params

    def set_params(self, **params: ParamValue) -> T.Self:
        """Set the model params in place.

        Returns:
            T.Self: instance of the model.
        """
        for key, value in params.items():
            setattr(self, key, value)
        return self

    @abc.abstractmethod
    def fit(self, inputs: schemas.Inputs, targets: schemas.Targets) -> T.Self:
        """Fit the model on the given inputs and targets.

        Args:
            inputs (schemas.Inputs): model training inputs.
            targets (schemas.Targets): model training targets.

        Returns:
            T.Self: instance of the model.
        """

    @abc.abstractmethod
    def predict(self, inputs: schemas.Inputs) -> schemas.Outputs:
        """Generate outputs with the model for the given inputs.

        Args:
            inputs (schemas.Inputs): model prediction inputs.

        Returns:
            schemas.Outputs: model prediction outputs.
        """

    def explain_model(self) -> schemas.FeatureImportances:
        """Explain the internal model structure.

        Raises:
            NotImplementedError: method not implemented.

        Returns:
            schemas.FeatureImportances: feature importances.
        """
        raise NotImplementedError()

    def explain_samples(self, inputs: schemas.Inputs) -> schemas.SHAPValues:
        """Explain model outputs on input samples.

        Raises:
            NotImplementedError: method not implemented.

        Returns:
            schemas.SHAPValues: SHAP values.
        """
        raise NotImplementedError()

    def get_internal_model(self) -> T.Any:
        """Return the internal model in the object.

        Raises:
            NotImplementedError: method not implemented.

        Returns:
            T.Any: any internal model (either empty or fitted).
        """
        raise NotImplementedError()


class BaselineSklearnModel(Model):
    """Simple baseline model based on scikit-learn.

    Parameters:
        max_depth (int): maximum depth of the random forest.
        n_estimators (int): number of estimators in the random forest.
        random_state (int, optional): random state of the machine learning pipeline.
    """

    KIND: T.Literal["BaselineSklearnModel"] = "BaselineSklearnModel"

    # params
    max_depth: int = 20
    n_estimators: int = 200
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

    @T.override
    def fit(self, inputs: schemas.Inputs, targets: schemas.Targets) -> "BaselineSklearnModel":
        # subcomponents
        categoricals_transformer = preprocessing.OneHotEncoder(
            sparse_output=False, handle_unknown="ignore"
        )
        # components
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
        # pipeline
        self._pipeline = pipeline.Pipeline(
            steps=[
                ("transformer", transformer),
                ("regressor", regressor),
            ]
        )
        self._pipeline.fit(X=inputs, y=targets[schemas.TargetsSchema.cnt])
        return self

    @T.override
    def predict(self, inputs: schemas.Inputs) -> schemas.Outputs:
        model = self.get_internal_model()
        prediction = model.predict(inputs)
        outputs = schemas.Outputs(
            {schemas.OutputsSchema.prediction: prediction}, index=inputs.index
        )
        return outputs

    @T.override
    def explain_model(self) -> schemas.FeatureImportances:
        model = self.get_internal_model()
        regressor = model.named_steps["regressor"]
        transformer = model.named_steps["transformer"]
        column_names = transformer.get_feature_names_out()
        feature_importances = schemas.FeatureImportances(
            data={
                "feature": column_names,
                "importance": regressor.feature_importances_,
            }
        )
        return feature_importances

    @T.override
    def explain_samples(self, inputs: schemas.Inputs) -> schemas.SHAPValues:
        model = self.get_internal_model()
        regressor = model.named_steps["regressor"]
        transformer = model.named_steps["transformer"]
        transformed = transformer.transform(X=inputs)
        explainer = shap.TreeExplainer(model=regressor)
        shap_values = schemas.SHAPValues(
            data=explainer.shap_values(X=transformed),
            columns=transformer.get_feature_names_out(),
        )
        return shap_values

    @T.override
    def get_internal_model(self) -> pipeline.Pipeline:
        model = self._pipeline
        if model is None:
            raise ValueError("Model is not fitted yet!")
        return model


ModelKind = BaselineSklearnModel
