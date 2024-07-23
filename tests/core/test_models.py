# %% IMPORTS

import typing as T

import pytest
from bikes.core import models, schemas

# %% MODELS


def test_model(inputs_samples: schemas.Inputs) -> None:
    # given
    class MyModel(models.Model):
        KIND: T.Literal["MyModel"] = "MyModel"

        # public
        a: int = 1
        b: int = 2
        # private
        _c: int = 3

        def fit(self, inputs: schemas.Inputs, targets: schemas.Targets) -> T.Self:
            return self

        def predict(self, inputs: schemas.Inputs) -> schemas.Outputs:
            return schemas.Outputs()

    # when
    model = MyModel(a=10)
    params_init = model.get_params()
    params_set_params = model.set_params(b=20).get_params()
    with pytest.raises(NotImplementedError) as explain_model_error:
        model.explain_model()
    with pytest.raises(NotImplementedError) as explain_samples_error:
        model.explain_samples(inputs=inputs_samples)
    with pytest.raises(NotImplementedError) as get_internal_model_error:
        model.get_internal_model()
    # then
    assert params_init == {"a": 10, "b": 2}, "Model should have the given params after init!"
    assert params_set_params == {
        "a": 10,
        "b": 20,
    }, "Model should have the given params after set_params!"
    assert isinstance(
        explain_model_error.value, NotImplementedError
    ), "Model should raise NotImplementedError for explain_model_error()!"
    assert isinstance(
        explain_samples_error.value, NotImplementedError
    ), "Model should raise NotImplementedError for explain_samples_error()!"
    assert isinstance(
        get_internal_model_error.value, NotImplementedError
    ), "Model should raise NotImplementedError for get_internal_model_error()!"


def test_baseline_sklearn_model(
    train_test_sets: tuple[schemas.Inputs, schemas.Targets, schemas.Inputs, schemas.Targets],
) -> None:
    # given
    params = {"max_depth": 3, "n_estimators": 5, "random_state": 0}
    inputs_train, targets_train, inputs_test, _ = train_test_sets
    model = models.BaselineSklearnModel().set_params(**params)
    # when
    with pytest.raises(ValueError) as not_fitted_error:
        model.get_internal_model()
    model.fit(inputs=inputs_train, targets=targets_train)
    outputs = model.predict(inputs=inputs_test)
    shap_values = model.explain_samples(inputs=inputs_test)
    feature_importances = model.explain_model()
    # then
    assert not_fitted_error.match(
        "Model is not fitted yet!"
    ), "Model should raise an error when not fitted!"
    # - model
    assert model.get_params() == params, "Model should have the given params!"
    assert model.get_internal_model() is not None, "Internal model should be fitted!"
    # - outputs
    assert outputs.ndim == 2, "Outputs should be a dataframe!"
    # - shap values
    assert len(shap_values.index) == len(
        inputs_test.index
    ), "SHAP values should be the same length as inputs!"
    assert len(shap_values.columns) >= len(
        inputs_test.columns
    ), "SHAP values should have more features than inputs!"
    # - feature importances
    assert (
        feature_importances["importance"].sum() == 1.0
    ), "Feature importances should add up to 1.0!"
    assert len(feature_importances["feature"]) >= len(
        inputs_train.columns
    ), "Feature importances should have more features than inputs!"
