# %% IMPORTS

import _pytest.capture as pc
import _pytest.logging as pl
import mlflow
import plyer
import pytest
import pytest_mock as pm

from bikes.io import services

# %% SERVICES


def test_logger_service(logger_service: services.LoggerService, logger_caplog: pl.LogCaptureFixture) -> None:
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
def test_alerts_service(enable: bool, mocker: pm.MockerFixture, capsys: pc.CaptureFixture[str]) -> None:
    # given
    service = services.AlertsService(enable=enable)
    mocker.patch(target="plyer.notification.notify")
    # when
    service.notify(title="test", message="hello")
    # then
    if enable:
        (
            plyer.notification.notify.assert_called_once(),
            "Notification method should be called!",
        )
        assert capsys.readouterr().out == "", "Notification should not be printed to stdout!"
    else:
        (
            plyer.notification.notify.assert_not_called(),
            "Notification method should not be called!",
        )
        assert capsys.readouterr().out == "[Bikes] test: hello\n", "Notification should be printed to stdout!"


def test_alerts_service__not_supported(mocker: pm.MockerFixture, capsys: pc.CaptureFixture[str]) -> None:
    # given
    def notify_not_supported(*args, **kwargs):
        raise NotImplementedError

    service = services.AlertsService(enable=True)
    mocker.patch(target="plyer.notification.notify", new=notify_not_supported)
    # when
    service.notify(title="test", message="hello")
    # then
    assert "Notifications are not supported on this system." in capsys.readouterr().out


@pytest.mark.parametrize(
    ("title", "message", "app_name", "expected_title", "expected_message", "expected_app_name"),
    [
        ("test", "hello", "Bikes", "test", "hello", "Bikes"),
        ("t" * 63, "m" * 255, "a" * 127, "t" * 63, "m" * 255, "a" * 127),
        ("t" * 64, "m" * 376, "a" * 128, "t" * 62 + "…", "m" * 254 + "…", "a" * 126 + "…"),
        ("😀" * 32, "😀" * 128, "😀" * 64, "😀" * 31 + "…", "😀" * 127 + "…", "😀" * 63 + "…"),
        ("t" + "😀" * 32, "m" * 376, "a" * 128, "t" + "😀" * 30 + "…", "m" * 254 + "…", "a" * 126 + "…"),
    ],
)
def test_alerts_service__windows_limits(
    mocker: pm.MockerFixture,
    title: str,
    message: str,
    app_name: str,
    expected_title: str,
    expected_message: str,
    expected_app_name: str,
) -> None:
    # given
    mocker.patch("bikes.io.services.sys.platform", "win32")
    service = services.AlertsService(enable=True, app_name=app_name)
    notify = mocker.patch(target="plyer.notification.notify")
    # when
    service.notify(title=title, message=message)
    # then
    notify.assert_called_once_with(
        title=expected_title,
        message=expected_message,
        app_name=expected_app_name,
        timeout=None,
    )
    for field, limit in [(expected_title, 63), (expected_message, 255), (expected_app_name, 127)]:
        assert len(field.encode("utf-16-le")) // 2 <= limit


@pytest.mark.parametrize("platform", ["linux", "darwin"])
def test_alerts_service__long_fields_on_other_platforms(platform: str, mocker: pm.MockerFixture) -> None:
    mocker.patch("bikes.io.services.sys.platform", platform)
    service = services.AlertsService(app_name="a" * 128)
    notify = mocker.patch("plyer.notification.notify")
    service.notify(title="t" * 64, message="m" * 376)
    notify.assert_called_once_with(title="t" * 64, message="m" * 376, app_name="a" * 128, timeout=None)


@pytest.mark.parametrize("enable", [True, False])
def test_alerts_service__windows_fallback_keeps_long_fields(
    enable: bool, mocker: pm.MockerFixture, capsys: pc.CaptureFixture[str]
) -> None:
    mocker.patch("bikes.io.services.sys.platform", "win32")
    notify = mocker.patch("plyer.notification.notify", side_effect=NotImplementedError)
    service = services.AlertsService(enable=enable, app_name="a" * 128)
    service.notify(title="t" * 64, message="m" * 376)
    assert f"[{'a' * 128}] {'t' * 64}: {'m' * 376}\n" in capsys.readouterr().out
    assert notify.call_count == int(enable)


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
    assert run_config.description in context.data.tags.values(), "Context desc. should be in tags values!"
    assert context.data.tags.items() > run_config.tags.items(), "Context tags should be a subset of the given tags!"
    assert context.info.status == "RUNNING", "Context should be running!"
    # - finished
    assert finished.info.status == "FINISHED", "Finished should be finished!"
