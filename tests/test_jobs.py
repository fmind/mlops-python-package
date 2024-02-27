# %% IMPORTS

import os

from bikes import datasets, jobs, metrics, models, registers, searchers, services, splitters

# %% JOBS


def test_tuning_job(
    inputs_reader: datasets.Reader,
    targets_reader: datasets.Reader,
    tmp_results_writer: datasets.ParquetWriter,
    default_model: models.Model,
    default_metric: metrics.Metric,
    default_searcher: searchers.GridCVSearcher,
    time_series_splitter: splitters.TimeSeriesSplitter,
    logger_service: services.LoggerService,
    carbon_service: services.CarbonService,
    mlflow_service: services.MLflowService,
):
    # given
    run_name = "TuningTest"
    job = jobs.TuningJob(
        run_name=run_name,
        inputs=inputs_reader,
        targets=targets_reader,
        results=tmp_results_writer,
        model=default_model,
        metric=default_metric,
        searcher=default_searcher,
        splitter=time_series_splitter,
        logger_service=logger_service,
        carbon_service=carbon_service,
        mlflow_service=mlflow_service,
    )
    mlflow_client = mlflow_service.client()
    n_trials = sum(len(vs) for vs in default_searcher.param_grid.values())
    # when
    with job as runner:
        out = runner.run()
    # then
    # - vars
    assert set(out) == {
        "self",
        "run",
        "inputs",
        "targets",
        "results",
        "best_score",
        "best_params",
    }
    # - run
    assert out["run"].info.run_name == run_name, "Run name should be the same!"
    # - read
    assert out["inputs"].ndim == 2, "Inputs should be a dataframe!"
    assert out["targets"].ndim == 2, "Target should be a dataframe!"
    # - search
    assert len(out["results"]) == n_trials, "Results should one row per candidate!"
    assert float("-inf") <= out["best_score"] <= float("+inf"), "Best score should be a float!"
    assert (
        out["best_params"].keys() == default_searcher.param_grid.keys()
    ), "Best params should have the same keys!"
    # - write
    assert os.path.exists(tmp_results_writer.path), "Results should be saved to the given path!"
    # - mlflow tracking
    mlflow_experiment = mlflow_client.get_experiment_by_name(name=mlflow_service.experiment_name)
    assert (
        mlflow_experiment.name == mlflow_service.experiment_name
    ), "Mlflow experiment name should be the same!"
    mlflow_runs = mlflow_client.search_runs(experiment_ids=mlflow_experiment.experiment_id)
    assert (
        len(mlflow_runs) == n_trials + 1
    ), "There should be as many Mlflow runs as trials + 1 for parent!"


def test_training_job(
    inputs_reader: datasets.Reader,
    targets_reader: datasets.Reader,
    default_saver: registers.Saver,
    empty_model: models.Model,
    default_metric: metrics.Metric,
    default_signer: registers.Signer,
    train_test_splitter: splitters.TrainTestSplitter,
    logger_service: services.LoggerService,
    carbon_service: services.CarbonService,
    mlflow_service: services.MLflowService,
):
    # given
    run_name = "TrainingTest"
    scorers = [default_metric]
    registry_alias = "Testing"
    job = jobs.TrainingJob(
        run_name=run_name,
        inputs=inputs_reader,
        targets=targets_reader,
        saver=default_saver,
        model=empty_model,
        signer=default_signer,
        scorers=scorers,
        splitter=train_test_splitter,
        registry_alias=registry_alias,
        logger_service=logger_service,
        carbon_service=carbon_service,
        mlflow_service=mlflow_service,
    )
    mlflow_client = mlflow_service.client()
    # when
    with job as runner:
        out = runner.run()
    # then
    # - vars
    assert set(out) == {
        "self",
        "run",
        "inputs",
        "targets",
        "train_index",
        "test_index",
        "inputs_train",
        "inputs_test",
        "targets_train",
        "targets_test",
        "outputs_test",
        "scorer",
        "score",
        "i",
        "signature",
        "info",
        "version",
    }
    # - run
    assert out["run"].info.run_name == run_name, "Run name should be the same!"
    # - read
    assert out["inputs"].ndim == 2, "Inputs should be a dataframe!"
    assert out["targets"].ndim == 2, "Target should be a dataframe!"
    # - split
    assert (
        len(out["train_index"]) + len(out["test_index"])
        == len(out["inputs"])
        == len(out["targets"])
    ), "Train and test indexes should have the same length as inputs! and targets!"
    assert (
        len(out["inputs_train"]) == len(out["targets_train"]) == len(out["train_index"])
    ), "Inputs and targets train should have the same length as train index!"
    assert (
        len(out["inputs_test"]) == len(out["targets_test"]) == len(out["test_index"])
    ), "Inputs and targets test should have the same length as test index!"
    # - outputs
    assert len(out["outputs_test"]) == len(
        out["inputs_test"]
    ), "Outputs should have the same length as inputs!"
    assert (
        out["outputs_test"].shape == out["targets_test"].shape
    ), "Outputs should have the same shape as targets!"
    # - score
    assert out["i"] == len(scorers), "i should have the same length as scorers!"
    assert (
        float("-inf") <= out["score"] <= float("+inf")
    ), "Score should be between a numeric value!"
    # - signature
    assert out["signature"].inputs is not None, "Signature inputs should not be None!"
    assert out["signature"].outputs is not None, "Signature outputs should not be None!"
    # - info
    assert out["info"].run_id == out["run"].info.run_id, "Info run id should be the same!"
    assert out["info"].signature == out["signature"], "Info signatures should be the same!"
    assert out["info"].artifact_path == default_saver.path, "Info path should be the same!"
    # - version
    assert out["version"].version == 1, "Version number should be 1!"
    assert out["version"].run_id == out["run"].info.run_id, "Version run id should be the same!"
    # - mlflow tracking
    mlflow_experiment = mlflow_client.get_experiment_by_name(name=mlflow_service.experiment_name)
    assert (
        mlflow_experiment.name == mlflow_service.experiment_name
    ), "MLflow Experiment name should be the same!"
    mlflow_runs = mlflow_client.search_runs(experiment_ids=mlflow_experiment.experiment_id)
    assert len(mlflow_runs) == 1, "There should be a single MLflow run for the training!"
    # - mlflow registry
    model_version = mlflow_client.get_model_version(
        name=mlflow_service.registry_name, version=out["version"].version
    )
    assert (
        model_version.run_id == out["run"].info.run_id
    ), "MLFlow model version run id should be the same!"


def test_inference_job(
    inputs_reader: datasets.ParquetReader,
    tmp_outputs_writer: datasets.ParquetWriter,
    default_loader: registers.Loader,
    default_alias: str,
    default_mlflow_model_version: registers.Version,
    logger_service: services.LoggerService,
    carbon_service: services.CarbonService,
    mlflow_service: services.MLflowService,
):
    # given
    registry_alias = "Testing"
    job = jobs.InferenceJob(
        inputs=inputs_reader,
        outputs=tmp_outputs_writer,
        registry_alias=default_alias,
        loader=default_loader,
        logger_service=logger_service,
        carbon_service=carbon_service,
        mlflow_service=mlflow_service,
    )
    # when
    with job as runner:
        out = runner.run()
    # then
    # - vars
    assert set(out) == {
        "self",
        "inputs",
        "uri",
        "model",
        "outputs",
    }
    # - inputs
    assert out["inputs"].ndim == 2, "Inputs should be a dataframe!"
    # - uri
    assert mlflow_service.registry_name in out["uri"], "URI should contain the registry name!"
    assert registry_alias in out["uri"], "URI should contain the registry alias!"
    # - model
    assert out["model"].metadata.signature is not None, "Model should have a valid signature!"
    assert out["model"].metadata.flavors.get(
        "python_function"
    ), "Model should have a pyfunc flavor!"
    assert (
        out["model"].metadata.run_id == default_mlflow_model_version.run_id
    ), "Model run id should be the same!"
    # - outputs
    assert os.path.exists(tmp_outputs_writer.path), "Outputs should be saved to the given path!"
