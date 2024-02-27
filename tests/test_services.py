# %% IMPORTS

import os

import mlflow
from bikes import services
from loguru import logger

# %% SERVICES


def test_logger_service(capsys):
    # given
    service = services.LoggerService(sink="stdout", level="INFO")
    # when
    service.start()
    logger.info("INFO")
    logger.debug("DEBUG")
    # then
    capture = capsys.readouterr()
    assert capture.err == "", "No output to stderr!"
    assert "INFO" in capture.out, "INFO should be logged!"
    assert "DEBUG" not in capture.out, "Debug should not be logged!"


def test_carbon_service(tmp_carbon_path: str):
    # given
    output_dir = tmp_carbon_path
    output_file = "emissions-test.csv"
    output_path = os.path.join(output_dir, output_file)
    service = services.CarbonService(output_dir=output_dir, output_file=output_file)
    # when
    service.start()
    service.stop()
    # then
    assert os.path.exists(output_path), "Output path should be created!"
    assert os.stat(output_path).st_size > 0, "Output path should not be empty!"


def test_mlflow_service(mlflow_service: services.MLflowService):
    # given
    service = mlflow_service
    # when
    service.start()
    client = service.client()
    service.stop()  # no effect
    # then
    # - mlflow
    assert (
        mlflow_service.tracking_uri == mlflow.get_tracking_uri()
    ), "Tracking URI should be the same!"
    assert (
        mlflow_service.registry_uri == mlflow.get_registry_uri()
    ), "Registry URI should be the same!"
    assert mlflow.get_experiment_by_name(
        mlflow_service.experiment_name
    ), "Experiment should be setup!"
    # - client
    assert mlflow_service.tracking_uri == client.tracking_uri, "Tracking URI should be the same!"
    assert mlflow_service.registry_uri == client._registry_uri, "Tracking URI should be the same!"
    assert client.get_experiment_by_name(
        mlflow_service.experiment_name
    ), "Experiment should be setup!"
