# %% IMPORTS

import _pytest.capture as pc
import pytest
from bikes import jobs
from bikes.core import metrics, schemas
from bikes.io import datasets, registries, services

# %% JOBS


@pytest.mark.parametrize(
    "alias_or_version, thresholds",
    [
        (
            1,
            {
                "mean_squared_error": metrics.Threshold(
                    threshold=float("inf"), greater_is_better=False
                )
            },
        ),
        (
            "Promotion",
            {"r2_score": metrics.Threshold(threshold=-1, greater_is_better=True)},
        ),
        pytest.param(
            "Promotion",
            {"r2_score": metrics.Threshold(threshold=100, greater_is_better=True)},
            marks=pytest.mark.xfail(
                reason="Invalid threshold for metric.",
                raises=metrics.MlflowModelValidationFailedException,
            ),
        ),
    ],
)
def test_evaluations_job(
    alias_or_version: str | int,
    thresholds: dict[str, metrics.Threshold],
    mlflow_service: services.MlflowService,
    alerts_service: services.AlertsService,
    logger_service: services.LoggerService,
    inputs_reader: datasets.ParquetReader,
    targets_reader: datasets.ParquetReader,
    model_alias: registries.Version,
    metric: metrics.Metric,
    capsys: pc.CaptureFixture[str],
) -> None:
    # given
    if isinstance(alias_or_version, int):
        assert alias_or_version == model_alias.version, "Model version should be the same!"
    else:
        assert alias_or_version == model_alias.aliases[0], "Model alias should be the same!"
    run_config = mlflow_service.RunConfig(
        name="EvaluationsTest", tags={"context": "evaluations"}, description="Evaluations job."
    )
    # when
    job = jobs.EvaluationsJob(
        logger_service=logger_service,
        alerts_service=alerts_service,
        mlflow_service=mlflow_service,
        run_config=run_config,
        inputs=inputs_reader,
        targets=targets_reader,
        alias_or_version=alias_or_version,
        metrics=[metric],
        thresholds=thresholds,
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
        "dataset",
        "model_uri",
        "extra_metrics",
        "validation_thresholds",
        "evaluations",
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
    # - dataset
    assert out["dataset"].name == "evaluation", "Dataset name should be evaluation!"
    assert out["dataset"].predictions is None, "Dataset predictions should be None!"
    assert (
        out["dataset"].targets == schemas.TargetsSchema.cnt
    ), "Dataset targets should be the target column!"
    assert (
        inputs_reader.path in out["dataset"].source.uri
    ), "Dataset source should contain the inputs path!"
    assert (
        targets_reader.path in out["dataset"].source.uri
    ), "Dataset source should contain the targets path!"
    # - model uri
    assert str(alias_or_version) in out["model_uri"], "Model URI should contain the model alias!"
    assert (
        mlflow_service.registry_name in out["model_uri"]
    ), "Model URI should contain the registry name!"
    # - extra metrics
    assert len(out["extra_metrics"]) == len(
        job.metrics
    ), "Extra metrics should have the same length as metrics!"
    assert (
        out["extra_metrics"][0].name == job.metrics[0].name
    ), "Extra metrics name should be the same!"
    assert (
        out["extra_metrics"][0].greater_is_better == job.metrics[0].greater_is_better
    ), "Extra metrics greatter is better should be the same!"
    # - validation thresholds
    assert (
        out["validation_thresholds"].keys() == thresholds.keys()
    ), "Validation thresholds should have the same keys as thresholds!"
    # - evaluations
    assert (
        out["evaluations"].metrics["example_count"] == inputs_reader.limit
    ), "Evaluations should have the same number of examples as the inputs!"
    assert job.metrics[0].name in out["evaluations"].metrics, "Metric should be logged in Mlflow!"
    # - mlflow tracking
    experiment = mlflow_service.client().get_experiment_by_name(name=mlflow_service.experiment_name)
    assert (
        experiment.name == mlflow_service.experiment_name
    ), "Mlflow Experiment name should be the same!"
    runs = mlflow_service.client().search_runs(experiment_ids=experiment.experiment_id)
    assert len(runs) == 2, "There should be a two Mlflow run for training and evaluations!"
    assert metric.name in runs[0].data.metrics, "Metric should be logged in Mlflow!"
    assert runs[0].info.status == "FINISHED", "Mlflow run status should be set as FINISHED!"
    # - alerting service
    assert "Evaluations" in capsys.readouterr().out, "Alerting service should be called!"
