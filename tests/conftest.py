"""Configuration for the tests."""

# pylint: disable=redefined-outer-name

# %% IMPORTS

import os
import typing as T

import omegaconf
import pytest

from bikes import datasets, metrics, models, schemas, services, splitters

# %% FIXTURES

# %% - Paths


@pytest.fixture(scope="session")
def tests_path() -> str:
    """Return the path of the tests folder."""
    file = os.path.abspath(__file__)
    parent = os.path.dirname(file)
    return parent


@pytest.fixture(scope="session")
def tests_data_path(tests_path: str) -> str:
    """Return the path of the tests data folder."""
    return os.path.join(tests_path, "data")


@pytest.fixture(scope="session")
def tests_confs_path(tests_path: str) -> str:
    """Return the path of the tests confs folder."""
    return os.path.join(tests_path, "confs")


@pytest.fixture(scope="session")
def tests_inputs_path(tests_data_path: str) -> str:
    """Return the path of the tests inputs dataset."""
    return os.path.join(tests_data_path, "inputs.parquet")


@pytest.fixture(scope="session")
def tests_targets_path(tests_data_path: str) -> str:
    """Return the path of the tests targets dataset."""
    return os.path.join(tests_data_path, "targets.parquet")


@pytest.fixture(scope="session")
def tests_outputs_path(tests_data_path: str) -> str:
    """Return the path of the tests_ outputs dataset."""
    return os.path.join(tests_data_path, "outputs.parquet")


@pytest.fixture(scope="session")
def tests_model_path(tests_models_path: str) -> str:
    """Return the path of the tests model file."""
    return os.path.join(tests_models_path, "model.joblib")


@pytest.fixture(scope="function")
def tmp_outputs_path(tmp_path: str) -> str:
    """Return a path for the tmp outputs dataset."""
    return os.path.join(tmp_path, "outputs.parquet")


@pytest.fixture(scope="function")
def tmp_results_path(tmp_path: str) -> str:
    """Return a path of the tmp results dataset."""
    return os.path.join(tmp_path, "results.parquet")


@pytest.fixture(scope="function")
def tmp_model_path(tmp_path: str) -> str:
    """Return a path of the tmp model object."""
    return os.path.join(tmp_path, "model.joblib")


# %% - Datasets


@pytest.fixture(scope="session")
def tests_inputs_reader(tests_inputs_path: str) -> datasets.ParquetReader:
    """Return a reader for the tests inputs dataset."""
    return datasets.ParquetReader(path=tests_inputs_path)


@pytest.fixture(scope="session")
def tests_targets_reader(tests_targets_path: str) -> datasets.ParquetReader:
    """Return a reader for the tests targets dataset."""
    return datasets.ParquetReader(path=tests_targets_path)


@pytest.fixture(scope="session")
def tests_outputs_reader(tests_outputs_path: str) -> datasets.ParquetReader:
    """Return a reader for the tests outputs dataset."""
    return datasets.ParquetReader(path=tests_outputs_path)


@pytest.fixture(scope="function")
def tmp_outputs_writer(tmp_outputs_path: str) -> datasets.ParquetWriter:
    """Return a writer for the tmp outputs dataset."""
    return datasets.ParquetWriter(path=tmp_outputs_path)


# %% - Dataframes


@pytest.fixture(scope="session")
def inputs(tests_inputs_reader: datasets.ParquetReader) -> schemas.Inputs:
    """Return the inputs data."""
    data = tests_inputs_reader.read()
    return schemas.InputsSchema.check(data)


@pytest.fixture(scope="session")
def targets(tests_targets_reader: datasets.ParquetReader) -> schemas.Targets:
    """Return the targets data."""
    data = tests_targets_reader.read()
    return schemas.TargetsSchema.check(data)


@pytest.fixture(scope="session")
def outputs(tests_outputs_reader: datasets.ParquetReader) -> schemas.Outputs:
    """Return the outputs data."""
    data = tests_outputs_reader.read()
    return schemas.OutputsSchema.check(data)


# %% - Splitters


@pytest.fixture(scope="session")
def train_test_splitter() -> splitters.TrainTestSplitter:
    """Return the default train test splitter."""
    return splitters.TrainTestSplitter()


@pytest.fixture(scope="session")
def train_test_split(train_test_splitter: splitters.TrainTestSplitter, inputs: schemas.Inputs) -> splitters.TrainTest:
    """Return the train and test indexes for the inputs dataframe."""
    return next(train_test_splitter.split(data=inputs))


@pytest.fixture(scope="session")
def train_test_sets(
    train_test_split: splitters.TrainTest, inputs: schemas.Inputs, targets: schemas.Targets
) -> tuple[schemas.Inputs, schemas.Targets, schemas.Inputs, schemas.Targets]:
    """Return the inputs/targets train and test sets from the train and test split."""
    train_index, test_index = train_test_split
    inputs_train, inputs_test = inputs.loc[train_index], inputs.loc[test_index]
    targets_train, targets_test = targets.loc[train_index], targets.loc[test_index]
    return inputs_train, targets_train, inputs_test, targets_test


# # %% - Models


@pytest.fixture(scope="session")
def empty_model() -> models.BaselineSklearnModel:
    """Return an empty model for testing."""
    return models.BaselineSklearnModel()


@pytest.fixture(scope="session")
def default_model(
    model: models.BaselineSklearnModel, inputs: schemas.Inputs, targets: schemas.Targets
) -> models.BaselineSklearnModel:
    """Return the default model."""
    model.fit(inputs=inputs, targets=targets)
    # outputs = model.predict(inputs=inputs)
    # outputs.to_parquet("data/outputs.parquet")
    # outputs.to_parquet("tests/data/outputs.parquet")
    return model


# %% - Metrics


@pytest.fixture(scope="session")
def default_metric() -> metrics.SklearnMetric:
    """Return the default metric."""
    return metrics.SklearnMetric()


# %% - Services


@pytest.fixture(scope="session", autouse=True)
def logger_service():
    """Return and start the logger service."""
    service = services.LoggerService(colorize=False, diagnose=True)
    service.start()  # ready to be used
    return service


# # %% - Resolvers


# @pytest.fixture(scope="function", autouse=True)
# def tmp_path_resolver(tmp_path: str) -> T.Callable[[], str]:
#     """Register the tmp_path resolver with Omegaconf."""

#     def tmp_path_resolver() -> str:
#         """Return tmp_path."""
#         return tmp_path

#     # usage: enable the variable "${tmp_path:}" in the config files
#     omegaconf.OmegaConf.register_new_resolver("tmp_path", tmp_path_resolver, replace=True)
#     return tmp_path_resolver
