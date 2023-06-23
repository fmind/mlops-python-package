"""Configuration for the tests."""
# pylint: disable=redefined-outer-name

# %% IMPORTS

import os
import typing as T

import omegaconf
import pytest

from wines import datasets, metrics, models, schemas, services, splitters

# %% FIXTURES

# %% - Paths


@pytest.fixture(scope="session")
def test_path() -> str:
    """Return the path of the test folder."""
    file = os.path.abspath(__file__)
    parent = os.path.dirname(file)
    return parent


@pytest.fixture(scope="session")
def data_path(test_path: str) -> str:
    """Return the path of the data folder."""
    return os.path.join(test_path, "data")


@pytest.fixture(scope="session")
def confs_path(test_path: str) -> str:
    """Return the path of the confs folder."""
    return os.path.join(test_path, "confs")


@pytest.fixture(scope="session")
def models_path(test_path: str) -> str:
    """Return the path of the models folder."""
    return os.path.join(test_path, "models")


@pytest.fixture(scope="session")
def inputs_path(data_path: str) -> str:
    """Return the path of the inputs dataset."""
    return os.path.join(data_path, "inputs.parquet")


@pytest.fixture(scope="session")
def target_path(data_path: str) -> str:
    """Return the path of the target dataset."""
    return os.path.join(data_path, "target.parquet")


@pytest.fixture(scope="session")
def output_path(data_path: str) -> str:
    """Return the path of the output dataset."""
    return os.path.join(data_path, "output.parquet")


@pytest.fixture(scope="session")
def model_path(models_path: str) -> str:
    """Return the path of the output dataset."""
    return os.path.join(models_path, "model.joblib")


@pytest.fixture(scope="function")
def tmp_output_path(tmp_path: str) -> str:
    """Return a tmp path for the output dataset."""
    return os.path.join(tmp_path, "output.parquet")


@pytest.fixture(scope="function")
def tmp_results_path(tmp_path: str) -> str:
    """Return a tmp path of the results dataset."""
    return os.path.join(tmp_path, "results.csv")


@pytest.fixture(scope="function")
def tmp_model_path(tmp_path: str) -> str:
    """Return a tmp path of the model object."""
    return os.path.join(tmp_path, "model.joblib")


# %% - Datasets


@pytest.fixture(scope="session")
def inputs_dataset(inputs_path: str) -> datasets.ParquetDataset:
    """Return the dataset for the project inputs."""
    return datasets.ParquetDataset(path=inputs_path)


@pytest.fixture(scope="session")
def target_dataset(target_path: str) -> datasets.ParquetDataset:
    """Return the dataset for the project target."""
    return datasets.ParquetDataset(path=target_path)


@pytest.fixture(scope="session")
def output_dataset(output_path: str) -> datasets.ParquetDataset:
    """Return the dataset for the project output."""
    return datasets.ParquetDataset(path=output_path)


@pytest.fixture(scope="function")
def tmp_output_dataset(tmp_output_path: str) -> datasets.ParquetDataset:
    """Return a tmp dataset for the project output."""
    return datasets.ParquetDataset(path=tmp_output_path)


# %% - Dataframes


@pytest.fixture(scope="session")
def inputs(inputs_dataset: datasets.ParquetDataset) -> schemas.Inputs:
    """Return the inputs data."""
    data = inputs_dataset.read()
    return schemas.InputsSchema.check(data)


@pytest.fixture(scope="session")
def target(target_dataset: datasets.ParquetDataset) -> schemas.Target:
    """Return the target data."""
    data = target_dataset.read()
    return schemas.TargetSchema.check(data)


@pytest.fixture(scope="session")
def output(output_dataset: datasets.ParquetDataset) -> schemas.Output:
    """Return the output data."""
    data = output_dataset.read()
    return schemas.OutputSchema.check(data)


# %% - Splitters


@pytest.fixture(scope="session")
def default_splitter() -> splitters.Splitter:
    """Return the default splitter."""
    return splitters.TrainTestSplitter()


# %% - Subsets


@pytest.fixture(scope="session")
def train_test_sets(
    default_splitter: splitters.Splitter, inputs: schemas.Inputs, target: schemas.Target
) -> T.Tuple[schemas.Inputs, schemas.Inputs, schemas.Target, schemas.Target]:
    """Return the train and test sets for the inputs and target."""
    inputs_train, inputs_test = default_splitter.split(inputs)
    target_train, target_test = default_splitter.split(target)
    return (
        T.cast(schemas.Inputs, inputs_train),
        T.cast(schemas.Inputs, inputs_test),
        T.cast(schemas.Target, target_train),
        T.cast(schemas.Target, target_test),
    )


# %% - Models


@pytest.fixture(scope="session")
def default_model(inputs: schemas.Inputs, target: schemas.Target) -> models.BaselineSklearnModel:
    """Return the default model fitted."""
    model = models.BaselineSklearnModel()
    model.fit(inputs=inputs, target=target)
    # note: uncomment to save the model for test
    # model.save(path="tests/models/model.joblib")
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


# %% - Resolvers


@pytest.fixture(scope="function", autouse=True)
def tmp_path_resolver(tmp_path: str) -> T.Callable[[], str]:
    """Register the tmp_path resolver with Omegaconf."""

    def tmp_path_resolver() -> str:
        """Return tmp_path."""
        return tmp_path

    # usage: enable the variable "${tmp_path:}" in the config files
    omegaconf.OmegaConf.register_new_resolver("tmp_path", tmp_path_resolver, replace=True)
    return tmp_path_resolver
