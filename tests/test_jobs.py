"""Test the jobs module."""
# pylint: disable=missing-docstring

# %% IMPORTS

import os

from wines import datasets, jobs, metrics, models, schemas, searchers, splitters

# %% JOBS


def test_tuning_job(
    inputs_dataset: datasets.ParquetDataset,
    target_dataset: datasets.ParquetDataset,
    default_model: models.BaselineSklearnModel,
    default_metric: metrics.SklearnMetric,
    tmp_results_path: str,
):
    # given
    param_grid = {"max_depth": [2, 4], "n_estimators": [10, 15]}
    searcher = searchers.GridCVSearcher(param_grid=param_grid)
    # when
    job = jobs.TuningJob(
        inputs=inputs_dataset,
        target=target_dataset,
        model=default_model,
        metric=default_metric,
        searcher=searcher,
        output_results=tmp_results_path,
    )
    with job as runner:
        out = runner.run()
    # then
    # - vars
    assert set(out) == {
        "self",
        "inputs",
        "target",
        "results",
        "best_params",
        "best_score",
    }
    # - data
    assert out["inputs"].ndim == 2, "Inputs should be a dataframe!"
    assert out["target"].ndim == 2, "Target should be a dataframe!"
    # - search
    assert 0 <= out["best_score"] <= 1, "Best score should be between 0 and 1!"
    assert out["best_params"].keys() == param_grid.keys(), "Best params should have the same keys!"
    assert len(out["results"]) == 4, "Results data should have the same length as the number of candidate!"
    # - outputs
    assert os.path.exists(tmp_results_path), "Results should be saved to the given path!"


def test_training_job(
    inputs_dataset: datasets.ParquetDataset,
    target_dataset: datasets.ParquetDataset,
    default_metric: metrics.SklearnMetric,
    default_splitter: splitters.TrainTestSplitter,
    tmp_model_path: str,
):
    # given
    model = models.BaselineSklearnModel(max_depth=2, n_estimators=10)
    # when
    job = jobs.TrainingJob(
        inputs=inputs_dataset,
        target=target_dataset,
        model=model,
        metric=default_metric,
        splitter=default_splitter,
        output_model=tmp_model_path,
    )
    with job as runner:
        out = runner.run()
    # then
    # - vars
    assert set(out) == {
        "self",
        "inputs",
        "target",
        "inputs_train",
        "inputs_test",
        "target_train",
        "target_test",
        "output_test",
        "score",
    }
    # - data
    assert out["inputs"].ndim == 2, "Inputs should be a dataframe!"
    assert out["target"].ndim == 2, "Target should be a dataframe!"
    # - split
    assert len(out["inputs_train"]) + len(out["inputs_test"]) == len(
        out["inputs"]
    ), "Train and test inputs should have the same length as inputs!"
    assert len(out["target_train"]) + len(out["target_test"]) == len(
        out["target"]
    ), "Train and test target should have the same length as target!"
    assert len(out["inputs_train"]) == len(out["target_train"]), "Train inputs and target should have the same length!"
    assert len(out["inputs_test"]) == len(out["target_test"]), "Test inputs and target should have the same length!"
    # - output
    assert schemas.OutputSchema.check(out["output_test"]) is not None, "Output should be a valid!"
    assert len(out["output_test"]) == len(out["inputs_test"]), "Output should have the same length as inputs!"
    # - score
    assert 0 <= out["score"] <= 1, "Score should be between 0 and 1!"
    # - outputs
    assert os.path.exists(tmp_model_path), "Model should be saved to the given path!"


def test_inference_job(
    inputs_dataset: datasets.ParquetDataset,
    tmp_output_dataset: datasets.ParquetDataset,
    model_path: str,
):
    # when
    job = jobs.InferenceJob(
        inputs=inputs_dataset,
        output=tmp_output_dataset,
        model_path=model_path,
    )
    with job as runner:
        out = runner.run()
    # then
    # - vars
    assert set(out) == {
        "self",
        "inputs",
        "model",
        "output",
    }
    # - inputs
    assert out["inputs"].ndim == 2, "Inputs should be a dataframe!"
    # - model
    assert isinstance(out["model"], models.Model), "Model should be a valid instance!"
    # - output
    assert schemas.OutputSchema.check(out["output"]) is not None, "Output should be a valid!"
    assert os.path.exists(tmp_output_dataset.path), "Output should be saved to the given path!"
