import typing as T
from pathlib import Path

import pytest
import pytest_mock as pm

from bikes import jobs
from bikes.core import metrics, models, schemas
from bikes.io import datasets, registries, services
from bikes.utils import searchers, splitters


@pytest.fixture
def pipeline(
    tmp_path: Path,
    train_test_sets: tuple[schemas.Inputs, schemas.Targets, schemas.Inputs, schemas.Targets],
    mlflow_service: services.MlflowService,
    alerts_service: services.AlertsService,
    logger_service: services.LoggerService,
) -> jobs.PipelineJob:
    inputs_train, targets_train, inputs_test, targets_test = train_test_sets
    readers = {}
    for name, data in (
        ("inputs_train", inputs_train),
        ("targets_train", targets_train),
        ("inputs_test", inputs_test),
        ("targets_test", targets_test),
    ):
        path = tmp_path / f"{name}.parquet"
        data.to_parquet(path)
        readers[name] = datasets.ParquetReader(path=str(path))
    return jobs.PipelineJob(
        logger_service=logger_service,
        alerts_service=alerts_service,
        mlflow_service=mlflow_service,
        tuning=jobs.TuningJob(
            inputs=readers["inputs_train"],
            targets=readers["targets_train"],
            model=models.BaselineSklearnModel(n_estimators=3, random_state=23),
            splitter=splitters.TimeSeriesSplitter(n_splits=2, test_size=168),
            searcher=searchers.GridCVSearcher(param_grid={"max_depth": [1, 2]}, verbose=0),
        ),
        training=jobs.TrainingJob(
            inputs=readers["inputs_train"],
            targets=readers["targets_train"],
            model=models.BaselineSklearnModel(n_estimators=19, random_state=0),
            splitter=splitters.TrainTestSplitter(test_size=168),
        ),
        evaluations=jobs.EvaluationsJob(
            inputs=readers["inputs_test"],
            targets=readers["targets_test"],
            thresholds={"mean_squared_error": metrics.Threshold(threshold=1e9, greater_is_better=False)},
        ),
    )


@pytest.mark.parametrize("consumers", [False, True])
def test_pipeline_preserves_selected_parameters_and_version(
    pipeline: jobs.PipelineJob,
    consumers: bool,
    tmp_path: Path,
    mocker: pm.MockerFixture,
) -> None:
    if consumers:
        pipeline = jobs.PipelineJob.model_validate(
            pipeline.model_dump()
            | {
                "inference": jobs.InferenceJob(
                    inputs=pipeline.evaluations.inputs,
                    outputs=datasets.ParquetWriter(path=str(tmp_path / "outputs.parquet")),
                ),
                "explanations": jobs.ExplanationsJob(
                    inputs_samples=pipeline.evaluations.inputs,
                    models_explanations=datasets.ParquetWriter(path=str(tmp_path / "features.parquet")),
                    samples_explanations=datasets.ParquetWriter(path=str(tmp_path / "shap.parquet")),
                ),
            }
        )
    original = jobs.EvaluationsJob.run

    def register_competing_version(stage: jobs.EvaluationsJob) -> dict[str, T.Any]:
        client = stage.mlflow_service.client()
        candidate = client.get_model_version(stage.mlflow_service.registry_name, str(stage.alias_or_version))
        client.create_model_version(name=candidate.name, source=candidate.source, run_id=candidate.run_id)
        return original(stage)

    mocker.patch.object(jobs.EvaluationsJob, "run", autospec=True, side_effect=register_competing_version)
    with pipeline as runner:
        result = runner.run()
    version = result["version"]
    params = result["training"]["self"].model.get_params()
    assert params["max_depth"] == result["tuning"]["best_params"]["max_depth"]
    assert params["n_estimators"] == 3
    assert params["random_state"] == 23
    assert result["evaluations"]["self"].alias_or_version == version
    assert int(result["promotion"]["model_version"].version) == version
    assert result["evaluations"]["model_uri"].endswith(f"/{version}")
    client = pipeline.mlflow_service.client()
    assert int(client.get_model_version_by_alias(pipeline.mlflow_service.registry_name, "Champion").version) == version
    assert len(client.search_model_versions(f"name='{pipeline.mlflow_service.registry_name}'")) == 2
    training_run = client.get_run(result["training"]["run"].info.run_id)
    assert training_run.data.tags["tuning_run_id"] == result["tuning"]["run"].info.run_id
    artifacts = client.list_artifacts(result["tuning"]["run"].info.run_id)
    assert "selected_params.json" in {artifact.path for artifact in artifacts}
    loaded = result["evaluations"]["model"].model.unwrap_python_model().model
    assert loaded.get_params() == params
    if consumers:
        assert result["inference"]["self"].alias_or_version == version
        assert result["explanations"]["self"].alias_or_version == version
        assert (tmp_path / "outputs.parquet").exists()
        assert (tmp_path / "shap.parquet").exists()


def test_failed_evaluation_preserves_existing_champion(
    pipeline: jobs.PipelineJob,
    model_version: registries.Version,
) -> None:
    client = pipeline.mlflow_service.client()
    name = pipeline.mlflow_service.registry_name
    client.set_registered_model_alias(name=name, alias="Champion", version=model_version.version)
    config = pipeline.model_dump()
    config["evaluations"]["thresholds"] = {"r2_score": {"threshold": 100.0, "greater_is_better": True}}
    pipeline = jobs.PipelineJob.model_validate(config)
    with pipeline as runner, pytest.raises(metrics.MlflowModelValidationFailedException):
        runner.run()
    assert client.get_model_version_by_alias(name=name, alias="Champion").version == model_version.version
