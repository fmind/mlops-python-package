# %% IMPORTS

import os
import runpy
import warnings
from pathlib import Path

import mlflow
import pandas as pd
import pandera.errors as pe
import pytest
from mlflow.pyfunc import PythonModelContext

from bikes.core import models, schemas
from bikes.io import registries, services
from bikes.utils import signers

# %% HELPERS


def test_uri_for_model_alias() -> None:
    # given
    name = "testing"
    alias = "Champion"
    # when
    uri = registries.uri_for_model_alias(name=name, alias=alias)
    # then
    assert uri == f"models:/{name}@{alias}", "The model URI should be valid!"


def test_uri_for_model_version() -> None:
    # given
    name = "testing"
    version = 1
    # when
    uri = registries.uri_for_model_version(name=name, version=version)
    # then
    assert uri == f"models:/{name}/{version}", "The model URI should be valid!"


def test_uri_for_model_alias_or_version() -> None:
    # given
    name = "testing"
    alias = "Champion"
    version = 1
    # when
    alias_uri = registries.uri_for_model_alias_or_version(name=name, alias_or_version=alias)
    version_uri = registries.uri_for_model_alias_or_version(name=name, alias_or_version=version)
    # then
    assert alias_uri == registries.uri_for_model_alias(name=name, alias=alias), "The alias URI should be valid!"
    assert version_uri == registries.uri_for_model_version(name=name, version=version), (
        "The version URI should be valid!"
    )


# %% SAVERS/LOADERS/REGISTERS


def test_custom_saver_import_without_type_hint_warning() -> None:
    # MLflow inspects predict when the adapter class is defined, before logging.
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        runpy.run_path(registries.__file__)
    assert not any("Type hint used in the model" in str(warning.message) for warning in caught)


@pytest.fixture
def adapter(model: models.Model, tmp_path: str) -> registries.CustomSaver.Adapter:
    """Return an adapter loaded the way MLflow loads it: from params and a skops file."""
    path = os.path.join(tmp_path, "model.skops")
    model.save_internal_model(path=path)
    adapter = registries.CustomSaver.Adapter()
    adapter.load_context(context=PythonModelContext(artifacts={"model": path}, model_config=model.model_dump()))
    return adapter


def test_custom_saver_model_code() -> None:
    # MLflow runs this file to rebuild the adapter: it must register one through set_model.
    module = runpy.run_path(str(registries.CustomSaver.CODE))
    assert isinstance(module["ADAPTER"], registries.CustomSaver.Adapter), "Model code should define the adapter!"


def test_custom_saver_adapter_predict(
    adapter: registries.CustomSaver.Adapter, model: models.Model, inputs: schemas.Inputs
) -> None:
    assert adapter.model is not model, "The adapter should rebuild its own model!"
    assert adapter.model.get_params() == model.get_params(), "The rebuilt model should keep the params!"
    outputs = adapter.predict(context=None, model_input=pd.DataFrame(inputs))
    pd.testing.assert_frame_equal(outputs, model.predict(inputs=inputs))


def test_custom_saver_adapter_rejects_invalid_inputs(
    adapter: registries.CustomSaver.Adapter, inputs: schemas.Inputs
) -> None:
    invalid_inputs = pd.DataFrame(inputs).copy()
    invalid_inputs["hr"] = 24
    with pytest.raises(pe.SchemaError, match="less_than_or_equal_to"):
        adapter.predict(context=None, model_input=invalid_inputs)


def test_custom_pipeline(
    model: models.Model,
    inputs: schemas.Inputs,
    signature: signers.Signature,
    mlflow_service: services.MlflowService,
) -> None:
    # given
    path = "custom"
    name = "Custom"
    tags = {"registry": "mlflow"}
    saver = registries.CustomSaver(path=path)
    loader = registries.CustomLoader()
    register = registries.MlflowRegister(tags=tags)
    run_config = mlflow_service.RunConfig(name="Custom-Run")
    # when
    with mlflow_service.run_context(run_config=run_config) as run:
        info = saver.save(model=model, signature=signature, input_example=inputs)
        version = register.register(name=name, model_uri=info.model_uri)
    model_uri = registries.uri_for_model_version(name=name, version=version.version)
    adapter = loader.load(uri=model_uri)
    outputs = adapter.predict(inputs=inputs)
    # then
    # - uri
    assert model_uri == f"models:/{name}/{version.version}", "The model URI should be valid!"
    # - info
    assert info.run_id == run.info.run_id, "The run id should be the same!"
    assert info.name == path, "The logged model name should be the same!"
    assert info.signature == signature, "The model signature should be the same!"
    assert info.flavors.get("python_function"), "The model should have a pyfunc flavor!"
    # - files: the adapter is code and the internal model is skops, nothing is pickled
    files = {f.name for f in Path(mlflow.artifacts.download_artifacts(info.model_uri)).rglob("*")}
    assert {"pyfunc_model.py", "model.skops"} <= files, "The model should be saved as code and skops!"
    assert not any(file.endswith(".pkl") for file in files), "The model should not contain any pickle!"
    # - version
    assert version.name == name, "The model version name should be the same!"
    assert version.tags == tags, "The model version tags should be the same!"
    assert version.aliases == [], "The model version aliases should be empty!"
    assert version.run_id == run.info.run_id, "The model version run id should be the same!"
    # - adapter
    assert adapter.model.metadata.run_id == version.run_id, "The adapter model run id should be the same!"
    assert adapter.model.metadata.signature == signature, "The adapter model signature should be the same!"
    assert adapter.model.metadata.flavors.get("python_function") is not None, (
        "The adapter model should have a python_function flavor!"
    )
    # - output
    assert schemas.OutputsSchema.check(outputs) is not None, "Outputs should be valid!"
    # The serialized PyFunc must retain Pandera constraints beyond MLflow's column types.
    invalid_inputs = inputs.copy()
    invalid_inputs.loc[:, "hr"] = 24
    with pytest.raises(pe.SchemaError, match="less_than_or_equal_to"):
        adapter.predict(inputs=invalid_inputs)


def test_builtin_pipeline(
    model: models.Model,
    inputs: schemas.Inputs,
    signature: signers.Signature,
    mlflow_service: services.MlflowService,
) -> None:
    # given
    path = "builtin"
    name = "Builtin"
    flavor = "sklearn"
    tags = {"registry": "mlflow"}
    # the fixture is a random forest built by this test, so its tree storage is trusted
    kwargs = {"skops_trusted_types": ["sklearn.tree._tree.Tree"]}
    saver = registries.BuiltinSaver(path=path, flavor=flavor, kwargs=kwargs)
    loader = registries.BuiltinLoader()
    register = registries.MlflowRegister(tags=tags)
    run_config = mlflow_service.RunConfig(name="Builtin-Run")
    # when
    with mlflow_service.run_context(run_config=run_config) as run:
        info = saver.save(model=model, signature=signature, input_example=inputs)
        version = register.register(name=name, model_uri=info.model_uri)
    model_uri = registries.uri_for_model_version(name=name, version=version.version)
    adapter = loader.load(uri=model_uri)
    outputs = adapter.predict(inputs=inputs)
    # then
    # - uri
    assert model_uri == f"models:/{name}/{version.version}", "The model URI should be valid!"
    # - info
    assert info.run_id == run.info.run_id, "The run id should be the same!"
    assert info.name == path, "The logged model name should be the same!"
    assert info.signature == signature, "The model signature should be the same!"
    assert info.flavors.get("python_function"), "The model should have a pyfunc flavor!"
    assert info.flavors.get(flavor), f"The model should have a built-in model flavor: {flavor}!"
    # - version
    assert version.name == name, "The model version name should be the same!"
    assert version.tags == tags, "The model version tags should be the same!"
    assert version.aliases == [], "The model version aliases should be empty!"
    assert version.run_id == run.info.run_id, "The model version run id should be the same!"
    # - adapter
    assert adapter.model.metadata.run_id == version.run_id, "The adapter model run id should be the same!"
    assert adapter.model.metadata.signature == signature, "The adapter model signature should be the same!"
    assert adapter.model.metadata.flavors.get("python_function") is not None, (
        "The adapter model should have a python_function flavor!"
    )
    assert adapter.model.metadata.flavors.get(flavor), f"The model should have a built-in model flavor: {flavor}!"
    # - output
    assert schemas.OutputsSchema.check(outputs) is not None, "Outputs should be valid!"
