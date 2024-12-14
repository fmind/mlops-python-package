"""Define trainable machine learning models."""

# %% IMPORTS

import abc
import typing as T

import pydantic as pdt
import shap
import xgboost as xgb
from sklearn import compose, ensemble, pipeline

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

        Returns:
            schemas.FeatureImportances: feature importances.
        """
        raise NotImplementedError()

    def explain_samples(self, inputs: schemas.Inputs) -> schemas.SHAPValues:
        """Explain model outputs on input samples.

        Returns:
            schemas.SHAPValues: SHAP values.
        """
        raise NotImplementedError()

    def get_internal_model(self) -> T.Any:
        """Return the internal model in the object.

        Returns:
            T.Any: any internal model fitted in the object.
        """
        raise NotImplementedError()

    def get_feature_importances(self) -> list[float]:
        """Get the feature importances of the model.

        Returns:
            list[float]:
        """
        raise NotImplementedError()

    def get_input_feature_names(self) -> list[str]:
        """Get the input feature names of the model.

        Returns:
            list[str]: list of input features names.
        """
        raise NotImplementedError()

    def get_output_feature_names(self) -> list[str]:
        """Get the output feature names of the model.

        Returns:
            list[str]: list of output features names.
        """
        raise NotImplementedError()


class Pipeline(Model):
    """Model composed of multiple models."""

    # private
    _pipeline: pipeline.Pipeline | None = None

    @T.override
    def get_internal_model(self) -> pipeline.Pipeline:
        if model := self._pipeline:
            return model
        raise ValueError("Model is not fitted yet!")

    @T.override
    def explain_model(self) -> schemas.FeatureImportances:
        feature = self.get_output_feature_names()
        importance = self.get_feature_importances()
        feature_importances = schemas.FeatureImportances(
            data={
                "feature": feature,
                "importance": importance,
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
        shap_data = explainer.shap_values(X=transformed)
        shap_columns = self.get_output_feature_names()
        shap_values = schemas.SHAPValues(
            data=shap_data,
            columns=shap_columns,
        )
        return shap_values

    @T.override
    def get_feature_importances(self):
        model = self.get_internal_model()
        regressor = model.named_steps["regressor"]
        return regressor.feature_importances_

    @T.override
    def get_input_feature_names(self) -> list[str]:
        model = self.get_internal_model()
        transformer = model.named_steps["transformer"]
        input_features_names = transformer.feature_names_in_
        return input_features_names.tolist()

    @T.override
    def get_output_feature_names(self) -> list[str]:
        model = self.get_internal_model()
        transformer = model.named_steps["transformer"]
        output_features_names = transformer.get_feature_names_out()
        return output_features_names.tolist()


class SklearnModel(Pipeline):
    """Model based on the scikit-learn framework.

    Parameters:
        max_depth (int): maximum depth of the random forest.
        n_estimators (int): n of estimators in the random forest.
        random_state (int, optional): random state of the ML pipeline.
    """

    KIND: T.Literal["SklearnModel"] = "SklearnModel"

    # params
    max_depth: int = 20
    n_estimators: int = 200
    random_state: int | None = 42
    # private
    _exclude_features: list[str] = [schemas.InputsSchema.dteday]

    @T.override
    def fit(self, inputs: schemas.Inputs, targets: schemas.Targets) -> "SklearnModel":
        # components
        transformer = compose.ColumnTransformer(
            [
                ("excluded", "drop", self._exclude_features),
            ],
            remainder="passthrough",
        )
        regressor = ensemble.RandomForestRegressor(
            max_depth=self.max_depth,
            n_estimators=self.n_estimators,
            random_state=self.random_state,
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
        prediction = model.predict(X=inputs)
        outputs = schemas.Outputs(
            {schemas.OutputsSchema.prediction: prediction}, index=inputs.index
        )
        return outputs


class XGBoostModel(Pipeline):
    """Model based on the XGBoost framework.

    Parameters:
        max_depth (int): maximum depth of the random forest.
        n_estimators (int): n of estimators in the random forest.
        random_state (int, optional): random state of the ML pipeline.
    """

    KIND: T.Literal["XGBoostModel"] = "XGBoostModel"

    # params
    max_depth: int = 20
    n_estimators: int = 200
    random_state: int | None = 42
    # private
    _exclude_features: list[str] = [schemas.InputsSchema.dteday]

    @T.override
    def fit(self, inputs: schemas.Inputs, targets: schemas.Targets) -> "XGBoostModel":
        # components
        transformer = compose.ColumnTransformer(
            [
                ("excluded", "drop", self._exclude_features),
            ],
            remainder="passthrough",
        )
        regressor = xgb.XGBRegressor(
            max_depth=self.max_depth,
            n_estimators=self.n_estimators,
            random_state=self.random_state,
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
        prediction = model.predict(X=inputs)
        outputs = schemas.Outputs(
            {schemas.OutputsSchema.prediction: prediction}, index=inputs.index
        )
        return outputs


ModelKind = SklearnModel | XGBoostModel
