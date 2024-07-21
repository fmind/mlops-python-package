# %% IMPORTS

from bikes.io import services
from bikes.jobs import base

# %% JOBS


def test_job(
    logger_service: services.LoggerService,
    alerts_service: services.AlertsService,
    mlflow_service: services.MlflowService,
) -> None:
    # given
    class MyJob(base.Job):
        KIND: str = "MyJob"

        def run(self) -> base.Locals:
            a, b = 1, "test"
            return locals()

    job = MyJob(
        logger_service=logger_service, alerts_service=alerts_service, mlflow_service=mlflow_service
    )
    # when
    with job as runner:
        out = runner.run()
    # then
    # - inputs
    assert hasattr(job, "logger_service"), "Job should have an Logger service!"
    assert hasattr(job, "alerts_service"), "Job should have a alerter service!"
    assert hasattr(job, "mlflow_service"), "Job should have an Mlflow service!"
    # - outputs
    assert set(out) == {"self", "a", "b"}, "Run should return local variables!"
