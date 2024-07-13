# %% IMPORTS


import _pytest.capture as pc
from bikes import jobs
from bikes.core import models
from bikes.io import datasets, registries, services

# %% JOBS


def test_explanations_job(
    mlflow_service: services.MlflowService,
    alerts_service: services.AlertsService,
    logger_service: services.LoggerService,
    inputs_samples_reader: datasets.Reader,
    tmp_models_explanations_writer: datasets.Writer,
    tmp_samples_explanations_writer: datasets.Writer,
    model_alias: registries.Version,
    loader: registries.Loader,
    capsys: pc.CaptureFixture[str],
) -> None:
    # given
    assert len(model_alias.aliases) == 1, "Model should have one alias!"
    alias = model_alias.aliases[0]
    # when
    job = jobs.ExplanationsJob(
        logger_service=logger_service,
        alerts_service=alerts_service,
        mlflow_service=mlflow_service,
        inputs_samples=inputs_samples_reader,
        models_explanations=tmp_models_explanations_writer,
        samples_explanations=tmp_samples_explanations_writer,
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
        "inputs_samples",
        "model_uri",
        "model",
        "models_explanations",
        "samples_explanations",
    }
    # - inputs
    assert out["inputs_samples"].ndim == 2, "Inputs samples should be a dataframe!"
    # - model uri
    assert alias in out["model_uri"], "Model URI should contain the model alias!"
    assert (
        mlflow_service.registry_name in out["model_uri"]
    ), "Model URI should contain the registry name!"
    # - model
    assert isinstance(out["model"], models.Model), "Model should be an instance of a project Model!"
    # - model explanations
    assert len(out["models_explanations"].index) >= len(
        out["inputs_samples"].columns
    ), "Model explanations should have at least as many columns as inputs samples!"
    # - samples explanations
    assert len(out["samples_explanations"].index) == len(
        out["inputs_samples"].index
    ), "Samples explanations should have the same number of rows as inputs samples!"
    assert len(out["samples_explanations"].columns) >= len(
        out["inputs_samples"].columns
    ), "Samples explanations should have at least as many columns as inputs samples!"
    # - alerting service
    assert (
        "Explanations Job Finished" in capsys.readouterr().out
    ), "Alerting service should be called!"
