# pylint: disable=missing-docstring

# %% IMPORTS

import os

from bikes import datasets, jobs, metrics, models, searchers, serializers, splitters

# %% JOBS


def test_tuning_job(
    inputs_reader: datasets.Reader,
    targets_reader: datasets.Reader,
    tmp_results_writer: datasets.ParquetWriter,
    default_model: models.Model,
    default_metric: metrics.Metric,
    time_series_splitter: splitters.TimeSeriesSplitter,
):
    # given
    param_grid = {"max_depth": [2, 4], "n_estimators": [10, 15]}
    searcher = searchers.GridCVSearcher(param_grid=param_grid)
    job = jobs.TuningJob(
        inputs=inputs_reader,
        targets=targets_reader,
        results=tmp_results_writer,
        model=default_model,
        metric=default_metric,
        splitter=time_series_splitter,
        searcher=searcher,
    )
    # when
    with job as runner:
        out = runner.run()
    # then
    # - vars
    assert set(out) == {
        "self",
        "inputs",
        "targets",
        "results",
        "best_params",
        "best_score",
    }
    # - read
    assert out["inputs"].ndim == 2, "Inputs should be a dataframe!"
    assert out["targets"].ndim == 2, "Target should be a dataframe!"
    # - search
    assert float("-inf") <= out["best_score"] <= float("+inf"), "Best score should be a float!"
    assert out["best_params"].keys() == param_grid.keys(), "Best params should have the same keys!"
    assert len(out["results"]) == sum(map(len, param_grid.values())), "Results should one row per candidate!"
    # - write
    assert os.path.exists(tmp_results_writer.path), "Results should be saved to the given path!"


def test_training_job(
    inputs_reader: datasets.Reader,
    targets_reader: datasets.Reader,
    empty_model: models.Model,
    default_metric: metrics.Metric,
    train_test_splitter: splitters.TrainTestSplitter,
    model_serializer: serializers.JoblibModelSerializer,
):
    # given
    scorers = [default_metric]
    job = jobs.TrainingJob(
        inputs=inputs_reader,
        targets=targets_reader,
        model=empty_model,
        scorers=scorers,
        splitter=train_test_splitter,
        serializer=model_serializer,
    )
    # when
    with job as runner:
        out = runner.run()
    # then
    # - vars
    assert set(out) == {
        "self",
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
    }
    # - read
    assert out["inputs"].ndim == 2, "Inputs should be a dataframe!"
    assert out["targets"].ndim == 2, "Target should be a dataframe!"
    # - split
    assert (
        len(out["train_index"]) + len(out["test_index"]) == len(out["inputs"]) == len(out["targets"])
    ), "Train and test indexes should have the same length as inputs! and targets!"
    assert (
        len(out["inputs_train"]) == len(out["targets_train"]) == len(out["train_index"])
    ), "Inputs and targets train should have the same length as train index!"
    assert (
        len(out["inputs_test"]) == len(out["targets_test"]) == len(out["test_index"])
    ), "Inputs and targets test should have the same length as test index!"
    # - outputs
    assert len(out["outputs_test"]) == len(out["inputs_test"]), "Outputs should have the same length as inputs!"
    assert out["outputs_test"].shape == out["targets_test"].shape, "Outputs should have the same shape as targets!"
    # - score
    assert out["i"] == len(scorers), "i should have the same length as scorers!"
    assert float("-inf") <= out["score"] <= float("+inf"), "Score should be between a numeric value!"
    # - write
    assert os.path.exists(model_serializer.path), "Model should be saved to the given path!"


def test_inference_job(
    inputs_reader: datasets.ParquetReader,
    tmp_outputs_writer: datasets.ParquetWriter,
    model_deserializer: serializers.JoblibModelDeserializer,
):
    # given
    job = jobs.InferenceJob(
        inputs=inputs_reader,
        outputs=tmp_outputs_writer,
        deserializer=model_deserializer,
    )
    # when
    with job as runner:
        out = runner.run()
    # then
    # - vars
    assert set(out) == {
        "self",
        "inputs",
        "model",
        "outputs",
    }
    # - inputs
    assert out["inputs"].ndim == 2, "Inputs should be a dataframe!"
    # - model
    assert isinstance(out["model"], models.Model), "Model should be a valid instance!"
    # - outputs
    assert out["outputs"].ndim == 2, "Outputs should be a dataframe!"
    assert os.path.exists(tmp_outputs_writer.path), "Outputs should be saved to the given path!"
