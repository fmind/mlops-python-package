# %% IMPORTS

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
    assert alias_uri == registries.uri_for_model_alias(
        name=name, alias=alias
    ), "The alias URI should be valid!"
    assert version_uri == registries.uri_for_model_version(
        name=name, version=version
    ), "The version URI should be valid!"


# %% SAVERS/LOADERS/REGISTERS


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
    assert info.artifact_path == path, "The artifact path should be the same!"
    assert info.signature == signature, "The model signature should be the same!"
    assert info.flavors.get("python_function"), "The model should have a pyfunc flavor!"
    # - version
    assert version.name == name, "The model version name should be the same!"
    assert version.tags == tags, "The model version tags should be the same!"
    assert version.aliases == [], "The model version aliases should be empty!"
    assert version.run_id == run.info.run_id, "The model version run id should be the same!"
    # - adapter
    assert (
        adapter.model.metadata.run_id == version.run_id
    ), "The adapter model run id should be the same!"
    assert (
        adapter.model.metadata.signature == signature
    ), "The adapter model signature should be the same!"
    assert (
        adapter.model.metadata.flavors.get("python_function") is not None
    ), "The adapter model should have a python_function flavor!"
    # - output
    assert schemas.OutputsSchema.check(outputs) is not None, "Outputs should be valid!"


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
    saver = registries.BuiltinSaver(path=path, flavor=flavor)
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
    assert info.artifact_path == path, "The artifact path should be the same!"
    assert info.signature == signature, "The model signature should be the same!"
    assert info.flavors.get("python_function"), "The model should have a pyfunc flavor!"
    assert info.flavors.get(flavor), f"The model should have a built-in model flavor: {flavor}!"
    # - version
    assert version.name == name, "The model version name should be the same!"
    assert version.tags == tags, "The model version tags should be the same!"
    assert version.aliases == [], "The model version aliases should be empty!"
    assert version.run_id == run.info.run_id, "The model version run id should be the same!"
    # - adapter
    assert (
        adapter.model.metadata.run_id == version.run_id
    ), "The adapter model run id should be the same!"
    assert (
        adapter.model.metadata.signature == signature
    ), "The adapter model signature should be the same!"
    assert (
        adapter.model.metadata.flavors.get("python_function") is not None
    ), "The adapter model should have a python_function flavor!"
    assert adapter.model.metadata.flavors.get(
        flavor
    ), f"The model should have a built-in model flavor: {flavor}!"
    # - output
    assert schemas.OutputsSchema.check(outputs) is not None, "Outputs should be valid!"
