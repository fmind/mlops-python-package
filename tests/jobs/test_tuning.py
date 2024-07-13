# %% IMPORTS

import _pytest.capture as pc
from bikes import jobs
from bikes.core import metrics, models, schemas
from bikes.io import datasets, services
from bikes.utils import searchers, splitters

# %% JOBS


def test_tuning_job(
    mlflow_service: services.MlflowService,
    alerts_service: services.AlertsService,
    logger_service: services.LoggerService,
    inputs_reader: datasets.ParquetReader,
    targets_reader: datasets.ParquetReader,
    model: models.Model,
    metric: metrics.Metric,
    time_series_splitter: splitters.Splitter,
    searcher: searchers.Searcher,
    capsys: pc.CaptureFixture[str],
) -> None:
    # given
    run_config = mlflow_service.RunConfig(
        name="TuningTest", tags={"context": "tuning"}, description="Tuning job."
    )
    splitter = time_series_splitter
    client = mlflow_service.client()
    # when
    job = jobs.TuningJob(
        logger_service=logger_service,
        alerts_service=alerts_service,
        mlflow_service=mlflow_service,
        run_config=run_config,
        inputs=inputs_reader,
        targets=targets_reader,
        model=model,
        metric=metric,
        splitter=splitter,
        searcher=searcher,
    )
    with job as runner:
        out = runner.run()
    # then
    # - vars
    assert set(out) == {
        "self",
        "logger",
        "run",
        "inputs",
        "inputs_",
        "inputs_lineage",
        "targets",
        "targets_",
        "targets_lineage",
        "results",
        "best_params",
        "best_score",
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
    assert out["targets"].ndim == out["inputs_"].ndim == 2, "Targets should be a dataframe!"
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
    # - results
    assert out["results"].ndim == 2, "Results should be a dataframe!"
    # - best score
    assert (
        float("-inf") < out["best_score"] < float("inf")
    ), "Best score should be between -inf and +inf!"
    # - best params
    assert (
        out["best_params"].keys() == searcher.param_grid.keys()
    ), "Best params should have the same keys!"
    # - mlflow tracking
    experiment = client.get_experiment_by_name(name=mlflow_service.experiment_name)
    assert (
        experiment.name == mlflow_service.experiment_name
    ), "Mlflow experiment name should be the same!"
    runs = client.search_runs(experiment_ids=experiment.experiment_id)
    assert len(runs) == len(out["results"]) + 1, "Mlflow should have 1 run per result + parent!"
    # - alerting service
    assert "Tuning Job Finished" in capsys.readouterr().out, "Alerting service should be called!"
