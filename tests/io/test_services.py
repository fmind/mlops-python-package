# %% IMPORTS

import _pytest.capture as pc
import _pytest.logging as pl
import mlflow
import plyer
import pytest
import pytest_mock as pm
from bikes.io import services

# %% SERVICES


def test_logger_service(
    logger_service: services.LoggerService, logger_caplog: pl.LogCaptureFixture
) -> None:
    # given
    service = logger_service
    logger = service.logger()
    # when
    logger.debug("DEBUG")
    logger.error("ERROR")
    # then
    assert "DEBUG" in logger_caplog.messages, "Debug message should be logged!"
    assert "ERROR" in logger_caplog.messages, "Error message should be logged!"


@pytest.mark.parametrize("enable", [True, False])
def test_alerts_service(
    enable: bool, mocker: pm.MockerFixture, capsys: pc.CaptureFixture[str]
) -> None:
    # given
    service = services.AlertsService(enable=enable)
    mocker.patch("plyer.notification.notify")
    # when
    service.notify(title="test", message="hello")
    # then
    if enable:
        plyer.notification.notify.assert_called_once(), "Notification method should be called!"
        assert capsys.readouterr().out == "", "Notification should not be printed to stdout!"
    else:
        (
            plyer.notification.notify.assert_not_called(),
            "Notification method should not be called!",
        )
        assert (
            capsys.readouterr().out == "[Bikes] test: hello\n"
        ), "Notification should be printed to stdout!"


def test_mlflow_service(mlflow_service: services.MlflowService) -> None:
    # given
    service = mlflow_service
    run_config = mlflow_service.RunConfig(
        name="testing",
        tags={"service": "mlflow"},
        description="a test run.",
        log_system_metrics=True,
    )
    # when
    client = service.client()
    with service.run_context(run_config=run_config) as context:
        pass
    finished = client.get_run(run_id=context.info.run_id)
    # then
    # - run
    assert run_config.tags is not None, "Run config tags should be set!"
    # - mlflow
    assert service.tracking_uri == mlflow.get_tracking_uri(), "Tracking URI should be the same!"
    assert service.registry_uri == mlflow.get_registry_uri(), "Registry URI should be the same!"
    assert mlflow.get_experiment_by_name(service.experiment_name), "Experiment should be setup!"
    # - client
    assert service.tracking_uri == client.tracking_uri, "Tracking URI should be the same!"
    assert service.registry_uri == client._registry_uri, "Tracking URI should be the same!"
    assert client.get_experiment_by_name(service.experiment_name), "Experiment should be setup!"
    # - context
    assert context.info.run_name == run_config.name, "Context name should be the same!"
    assert (
        run_config.description in context.data.tags.values()
    ), "Context desc. should be in tags values!"
    assert (
        context.data.tags.items() > run_config.tags.items()
    ), "Context tags should be a subset of the given tags!"
    assert context.info.status == "RUNNING", "Context should be running!"
    # - finished
    assert finished.info.status == "FINISHED", "Finished should be finished!"
