# %% IMPORTS

import typing as T

from bikes import models, schemas

# %% MODELS


def test_model() -> None:
    # given
    class MyModel(models.Model):  # type: ignore
        KIND: T.Literal["MyModel"] = "MyModel"

        # public
        a: int = 1
        b: int = 2
        # private
        _c: int = 3

        def fit(self, inputs: schemas.Inputs, targets: schemas.Targets) -> T.Self:
            return self

        def predict(self, inputs: schemas.Inputs) -> schemas.Outputs:
            pass

    # when
    model = MyModel(a=10)
    params_init = model.get_params()
    params_set_params = model.set_params(b=20).get_params()
    # then
    assert params_init == {"a": 10, "b": 2}, "Model should get the right params at init!"
    assert params_set_params == {
        "a": 10,
        "b": 20,
    }, "Model should set the right params after set_params!"


def test_baseline_sklearn_model(
    train_test_sets: tuple[schemas.Inputs, schemas.Targets, schemas.Inputs, schemas.Targets],
) -> None:
    # given
    params = {"max_depth": 3, "n_estimators": 5, "random_state": 0}
    inputs_train, targets_train, inputs_test, _ = train_test_sets
    model = models.BaselineSklearnModel().set_params(**params)
    # when
    model.fit(inputs=inputs_train, targets=targets_train)
    outputs = model.predict(inputs=inputs_test)
    # then
    assert outputs.ndim == 2, "Outputs should be a dataframe!"
    assert model.get_params() == params, "Model should have the given params!"
