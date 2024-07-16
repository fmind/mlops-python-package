# %% IMPORTS

import _pytest.capture as pc
import pytest
from bikes import jobs
from bikes.io import datasets, registries, services

# %% JOBS


@pytest.mark.parametrize("alias_or_version", [1, "Promotion"])
def test_inference_job(
    alias_or_version: str | int,
    mlflow_service: services.MlflowService,
    alerts_service: services.AlertsService,
    logger_service: services.LoggerService,
    inputs_reader: datasets.Reader,
    tmp_outputs_writer: datasets.Writer,
    model_alias: registries.Version,
    loader: registries.Loader,
    capsys: pc.CaptureFixture[str],
) -> None:
    # given
    if isinstance(alias_or_version, int):
        assert alias_or_version == model_alias.version, "Model version should be the same!"
    else:
        assert alias_or_version == model_alias.aliases[0], "Model alias should be the same!"
    # when
    job = jobs.InferenceJob(
        logger_service=logger_service,
        alerts_service=alerts_service,
        mlflow_service=mlflow_service,
        inputs=inputs_reader,
        outputs=tmp_outputs_writer,
        alias_or_version=alias_or_version,
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
    assert str(alias_or_version) in out["model_uri"], "Model URI should contain the model alias!"
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
