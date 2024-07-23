# %% IMPORTS

import _pytest.capture as pc
from bikes import jobs
from bikes.core import metrics, models, schemas
from bikes.io import datasets, registries, services
from bikes.utils import signers, splitters

# %% JOBS


def test_training_job(
    mlflow_service: services.MlflowService,
    alerts_service: services.AlertsService,
    logger_service: services.LoggerService,
    inputs_reader: datasets.ParquetReader,
    targets_reader: datasets.ParquetReader,
    model: models.Model,
    metric: metrics.Metric,
    train_test_splitter: splitters.Splitter,
    saver: registries.Saver,
    signer: signers.Signer,
    register: registries.Register,
    capsys: pc.CaptureFixture[str],
) -> None:
    # given
    run_config = mlflow_service.RunConfig(
        name="TrainingTest", tags={"context": "training"}, description="Training job."
    )
    splitter = train_test_splitter
    client = mlflow_service.client()
    # when
    job = jobs.TrainingJob(
        logger_service=logger_service,
        alerts_service=alerts_service,
        mlflow_service=mlflow_service,
        run_config=run_config,
        inputs=inputs_reader,
        targets=targets_reader,
        model=model,
        metrics=[metric],
        splitter=splitter,
        saver=saver,
        signer=signer,
        registry=register,
    )
    with job as runner:
        out = runner.run()
    # then
    # - vars
    assert set(out) == {
        "self",
        "logger",
        "client",
        "run",
        "inputs",
        "inputs_",
        "inputs_lineage",
        "targets",
        "targets_",
        "targets_lineage",
        "train_index",
        "test_index",
        "inputs_test",
        "inputs_train",
        "inputs_test",
        "targets_train",
        "targets_test",
        "outputs_test",
        "i",
        "metric",
        "score",
        "model_signature",
        "model_info",
        "model_version",
    }
    # - run
    assert run_config.tags is not None, "Run config tags should be set!"
    assert out["run"].info.run_name == run_config.name, "Run name should be the same!"
    assert run_config.description in out["run"].data.tags.values(), "Run desc. should be tags!"
    assert (
        out["run"].data.tags.items() > run_config.tags.items()
    ), "Run tags should be a subset of tags!"
    # - data
    assert out["inputs"].ndim == out["inputs_"].ndim == 2, "Inputs should be a dataframe!"
    assert out["targets"].ndim == out["targets_"].ndim == 2, "Targets should be a dataframe!"
    # - lineage
    assert out["inputs_lineage"].name == "inputs", "Inputs lineage name should be inputs!"
    assert (
        out["inputs_lineage"].source.uri == inputs_reader.path
    ), "Inputs lineage source should be the inputs reader path!"
    assert out["targets_lineage"].name == "targets", "Targets lineage name should be targets!"
    assert (
        out["targets_lineage"].source.uri == targets_reader.path
    ), "Targets lineage source should be the targets reader path!"
    assert (
        out["targets_lineage"].targets == schemas.TargetsSchema.cnt
    ), "Targets lineage target should be cnt!"
    # - splitter
    assert len(out["inputs_train"]) + len(out["inputs_test"]) == len(
        out["inputs"]
    ), "Train and test inputs should have the same length as inputs!"
    assert len(out["targets_train"]) + len(out["targets_test"]) == len(
        out["targets"]
    ), "Train and test targets should have the same length as targets!"
    assert (
        len(out["train_index"]) == len(out["inputs_train"]) == len(out["targets_train"])
    ), "Train inputs and targets should have the same length!"
    assert (
        len(out["test_index"]) == len(out["inputs_test"]) == len(out["targets_test"])
    ), "Test inputs and targets should have the same length!"
    # - outputs
    assert (
        out["outputs_test"].shape == out["targets_test"].shape
    ), "Outputs should have the same shape as targets!"
    assert (
        len(out["test_index"]) == len(out["outputs_test"]) == len(out["inputs_test"])
    ), "Outputs should have the same length as inputs!"
    # - i and score
    assert out["i"] == len(job.metrics), "i should be the number of metrics computed!"
    assert float("-inf") < out["score"] < float("+inf"), "Score should be between 0 and 1!"
    # - model signature
    assert out["model_signature"].inputs is not None, "Model signature inputs should not be None!"
    assert out["model_signature"].outputs is not None, "Model signature outputs should not be None!"
    # - model info
    assert (
        out["model_info"].run_id == out["run"].info.run_id
    ), "Model info run id should be the same!"
    assert (
        out["model_info"].signature == out["model_signature"]
    ), "Model info signature should be the same!"
    assert out["model_info"].artifact_path == saver.path, "Model info path should be the same!"
    # - model version
    assert out["model_version"].version == 1, "Model version number should be 1!"
    assert out["model_version"].aliases == [], "Model version aliases should be empty!"
    assert out["model_version"].tags == register.tags, "Model version tags should be the same!"
    assert (
        out["model_version"].name == mlflow_service.registry_name
    ), "Model name should be the same!"
    assert (
        out["model_version"].run_id == out["run"].info.run_id
    ), "Model version run id should be the same!"
    # - mlflow tracking
    experiment = client.get_experiment_by_name(name=mlflow_service.experiment_name)
    assert (
        experiment.name == mlflow_service.experiment_name
    ), "Mlflow Experiment name should be the same!"
    runs = client.search_runs(experiment_ids=experiment.experiment_id)
    assert len(runs) == 1, "There should be a single Mlflow run for training!"
    assert metric.name in runs[0].data.metrics, "Metric should be logged in Mlflow!"
    assert runs[0].info.status == "FINISHED", "Mlflow run status should be set as FINISHED!"
    # - mlflow registry
    model_version = client.get_model_version(
        name=mlflow_service.registry_name, version=out["model_version"].version
    )
    assert (
        model_version.run_id == out["run"].info.run_id
    ), "MLFlow model version run id should be the same!"
    # - alerting service
    assert "Training Job Finished" in capsys.readouterr().out, "Alerting service should be called!"
