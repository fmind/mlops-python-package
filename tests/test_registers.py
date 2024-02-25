"""Test the registers module."""

# %% IMPORTS

import mlflow
from bikes import models, registers, schemas, services

# %% ADAPTERS


def test_custom_adapter(default_model: models.Model, inputs: schemas.Inputs):
    # given
    adapter = registers.CustomAdapter(model=default_model)
    # when
    outputs = adapter.predict(context=None, inputs=inputs)
    # then
    assert schemas.OutputsSchema.check(outputs) is not None, "Outputs should be valid!"


# %% SIGNERS


def test_infer_signer(inputs: schemas.Inputs, outputs: schemas.Outputs):
    # given
    signer = registers.InferSigner()
    # when
    signature = signer.sign(inputs=inputs, outputs=outputs)
    # then
    assert set(signature.inputs.input_names()) == set(
        inputs.columns
    ), "Signature inputs should contain input column names."
    assert set(signature.outputs.input_names()) == set(
        outputs.columns
    ), "Signature outputs should contain output column names."


# %% SAVERS


def test_custom_saver(
    inputs: schemas.Inputs, default_model: models.Model, default_signature: registers.Signature
):
    # given
    path = "custom"
    saver = registers.CustomSaver(path=path)
    # when
    with mlflow.start_run(run_name="Custom") as run:
        info = saver.save(model=default_model, signature=default_signature, input_example=inputs)
    # then
    assert info.run_id == run.info.run_id, "The run id should be the same!"
    assert info.artifact_path == path, "The artifact path should be the same!"
    assert info.flavors.get("python_function"), "The model should have a pyfunc!"
    assert info.signature == default_signature, "The model signature should be the same!"


# %% LOADERS


def test_custom_loader(
    inputs: schemas.Inputs,
    mlflow_service: services.MLflowService,
    default_mlflow_model_version: registers.Version,
):
    # given
    name = mlflow_service.registry_name
    version = default_mlflow_model_version.version
    uri = f"models:/{name}/{version}"
    loader = registers.CustomLoader()
    # when
    model = loader.load(uri=uri)
    outputs = model.predict(data=inputs)
    # then
    # # - model
    assert model.metadata.signature is not None, "The model should have a valid signature!"
    assert (
        model.metadata.run_id == default_mlflow_model_version.run_id
    ), "The model run id should be the same!"
    assert (
        model.metadata.flavors.get("python_function") is not None
    ), "The model should have a python_function flavor!"
    # - output
    assert schemas.OutputsSchema.check(outputs) is not None, "Outputs should be valid!"
