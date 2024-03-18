# %% IMPORTS

from bikes import jobs
from bikes.core import metrics, models
from bikes.io import datasets, services
from bikes.utils import searchers, splitters

# %% JOBS


def test_tuning_job(
    mlflow_service: services.MlflowService,
    logger_service: services.LoggerService,
    inputs_reader: datasets.Reader,
    targets_reader: datasets.Reader,
    model: models.Model,
    metric: metrics.Metric,
    time_series_splitter: splitters.Splitter,
    searcher: searchers.Searcher,
) -> None:
    # given
    run_config = mlflow_service.RunConfig(
        name="TuningTest", tags={"context": "tuning"}, description="Tuning job."
    )
    splitter = time_series_splitter
    client = mlflow_service.client()
    # when
    job = jobs.TuningJob(
        mlflow_service=mlflow_service,
        logger_service=logger_service,
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
        "targets",
        "targets_",
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
