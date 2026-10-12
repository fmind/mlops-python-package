# %% IMPORTS

import _pytest.capture as pc
import mlflow
import pydantic as pdt
import pytest

from bikes import jobs
from bikes.io import registries, services

# %% JOBS


@pytest.mark.parametrize(
    "version",
    [
        1,  # specific version
        pytest.param(
            2,
            marks=pytest.mark.xfail(
                reason="Version does not exist.",
                raises=mlflow.exceptions.MlflowException,
            ),
        ),
    ],
)
def test_promotion_job(
    version: int,
    mlflow_service: services.MlflowService,
    alerts_service: services.AlertsService,
    logger_service: services.LoggerService,
    model_version: registries.Version,
    capsys: pc.CaptureFixture[str],
) -> None:
    # given
    alias = "Testing"
    # when
    job = jobs.PromotionJob(
        logger_service=logger_service,
        alerts_service=alerts_service,
        mlflow_service=mlflow_service,
        version=version,
        alias=alias,
    )
    with job as runner:
        out = runner.run()
    # then
    # - vars
    assert set(out) == {
        "self",
        "logger",
        "client",
        "name",
        "version",
        "model_version",
    }
    # - name
    assert out["name"] == mlflow_service.registry_name, "Model name should be the same!"
    # - version
    assert out["version"] == model_version.version, "Version number should be the same!"
    # - model version
    assert out["model_version"].name == out["name"], "Model version name should be the same!"
    assert out["model_version"].version == out["version"], "Model version number should be the same!"
    assert out["model_version"].run_id == model_version.run_id, "Model version run id should be the same!"
    assert out["model_version"].aliases == [alias], "Model version aliases should contain the given alias!"
    # - alerting service
    assert "Promotion Job Finished" in capsys.readouterr().out, "Alerting service should be called!"


@pytest.mark.parametrize("version", [None, 0, -1, "1"])
def test_promotion_requires_positive_explicit_version(version: object) -> None:
    with pytest.raises(pdt.ValidationError):
        jobs.PromotionJob.model_validate({"version": version})
    with pytest.raises(pdt.ValidationError):
        jobs.PromotionJob.model_validate({})
