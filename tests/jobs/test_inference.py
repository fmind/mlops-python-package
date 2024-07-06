# %% IMPORTS


import _pytest.capture as pc
from bikes import jobs
from bikes.io import datasets, registries, services

# %% JOBS


def test_inference_job(
    mlflow_service: services.MlflowService,
    alerter_service: services.AlerterService,
    logger_service: services.LoggerService,
    inputs_reader: datasets.Reader,
    tmp_outputs_writer: datasets.Writer,
    model_alias: registries.Version,
    loader: registries.Loader,
    capsys: pc.CaptureFixture[str],
) -> None:
    # given
    assert len(model_alias.aliases) == 1, "Model should have one alias!"
    alias = model_alias.aliases[0]
    # when
    job = jobs.InferenceJob(
        logger_service=logger_service,
        alerter_service=alerter_service,
        mlflow_service=mlflow_service,
        inputs=inputs_reader,
        outputs=tmp_outputs_writer,
        alias=alias,
        loader=loader,
    )
    with job as runner:
        out = runner.run()
    # then
    # - vars
    assert set(out) == {
        "self",
        "logger",
        "inputs",
        "inputs_",
        "model_uri",
        "model",
        "outputs",
    }
    # - inputs
    assert out["inputs"].ndim == out["inputs_"].ndim == 2, "Inputs should be a dataframe!"
    # - model uri
    assert alias in out["model_uri"], "Model URI should contain the model alias!"
    assert (
        mlflow_service.registry_name in out["model_uri"]
    ), "Model URI should contain the registry name!"
    # - model
    assert (
        out["model"].model.metadata.run_id == model_alias.run_id
    ), "Model run id should be the same!"
    assert out["model"].model.metadata.signature is not None, "Model should have a signature!"
    assert out["model"].model.metadata.flavors.get(
        "python_function"
    ), "Model should have a pyfunc flavor!"
    # - outputs
    assert out["outputs"].ndim == 2, "Outputs should be a dataframe!"
    # - alerting service
    assert "Inference Job Finished" in capsys.readouterr().out, "Alerting service should be called!"
