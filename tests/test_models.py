"""Test the models module."""
# pylint: disable=missing-docstring

# %% IMPORTS

import typing as T

from wines import models, schemas

# %% MODELS


class MyModel(models.Model):
    KIND: T.Literal["MyModel"] = "MyModel"

    a: int = 1
    b: int = 2
    _c: int = 3

    def fit(self, inputs, target):
        print(inputs, target)

    def predict(self, inputs):
        print(inputs)


def test_model(tmp_model_path: str):
    # when
    model = MyModel(a=10)
    params_get = model.get_params()
    params_set = model.set_params(b=20).get_params()
    model.save(path=tmp_model_path)
    reloaded = models.Model.load(path=tmp_model_path)
    # then
    assert params_get == {"a": 10, "b": 2}, "Model should get the right parameters!"
    assert params_set == {"a": 10, "b": 20}, "Model should set the right parameters!"
    assert model == reloaded, "Model should be the same after saving and loading it!"


def test_baseline_sklearn_model(
    train_test_sets: T.Tuple[schemas.Inputs, schemas.Inputs, schemas.Target, schemas.Target]
):
    # given
    inputs_train, inputs_test, target_train, _ = train_test_sets
    params: models.Params = {"max_depth": 3, "n_estimators": 5, "random_state": 0}
    # when
    model = models.BaselineSklearnModel().set_params(**params)
    model.fit(inputs=inputs_train, target=target_train)
    output = model.predict(inputs=inputs_test)
    # then
    assert model.get_params() == params, "Model should have the given parameters!"
    assert schemas.OutputSchema.check(output) is not None, "The output data should be valid!"
