"""Configuration for the tests."""

# pylint: disable=redefined-outer-name

# %% IMPORTS

import os

import omegaconf
import pytest

from bikes import datasets, metrics, models, schemas, serializers, services, splitters

# %% CONFIGS

LIMIT = 1500
N_SPLITS = 3
TEST_SIZE = 24 * 7  # 1 week

# %% FIXTURES

# %% - Paths


@pytest.fixture(scope="session")
def tests_path() -> str:
    """Return the path of the tests folder."""
    file = os.path.abspath(__file__)
    parent = os.path.dirname(file)
    return parent


@pytest.fixture(scope="session")
def data_path(tests_path: str) -> str:
    """Return the path of the data folder."""
    return os.path.join(tests_path, "data")


@pytest.fixture(scope="session")
def confs_path(tests_path: str) -> str:
    """Return the path of the confs folder."""
    return os.path.join(tests_path, "confs")


@pytest.fixture(scope="session")
def inputs_path(data_path: str) -> str:
    """Return the path of the inputs dataset."""
    return os.path.join(data_path, "inputs.parquet")


@pytest.fixture(scope="session")
def targets_path(data_path: str) -> str:
    """Return the path of the targets dataset."""
    return os.path.join(data_path, "targets.parquet")


@pytest.fixture(scope="session")
def outputs_path(data_path: str) -> str:
    """Return the path of the outputs dataset."""
    return os.path.join(data_path, "outputs.parquet")


@pytest.fixture(scope="function")
def tmp_outputs_path(tmp_path: str) -> str:
    """Return a tmp path for the outputs dataset."""
    return os.path.join(tmp_path, "outputs.parquet")


@pytest.fixture(scope="function")
def tmp_results_path(tmp_path: str) -> str:
    """Return a tmp path of the results dataset."""
    return os.path.join(tmp_path, "results.parquet")


@pytest.fixture(scope="function")
def tmp_model_path(tmp_path: str) -> str:
    """Return a tmp path of the model object."""
    return os.path.join(tmp_path, "model.joblib")


# %% - Datasets


@pytest.fixture(scope="session")
def inputs_reader(inputs_path: str) -> datasets.ParquetReader:
    """Return a reader for the inputs dataset."""
    return datasets.ParquetReader(path=inputs_path, limit=LIMIT)


@pytest.fixture(scope="session")
def targets_reader(targets_path: str) -> datasets.ParquetReader:
    """Return a reader for the targets dataset."""
    return datasets.ParquetReader(path=targets_path, limit=LIMIT)


@pytest.fixture(scope="session")
def outputs_reader(outputs_path: str) -> datasets.ParquetReader:
    """Return a reader for the outputs dataset."""
    return datasets.ParquetReader(path=outputs_path, limit=LIMIT)


@pytest.fixture(scope="function")
def tmp_outputs_writer(tmp_outputs_path: str) -> datasets.ParquetWriter:
    """Return a writer for the tmp outputs dataset."""
    return datasets.ParquetWriter(path=tmp_outputs_path)


@pytest.fixture(scope="function")
def tmp_results_writer(tmp_results_path: str) -> datasets.ParquetWriter:
    """Return a writer for the tmp results dataset."""
    return datasets.ParquetWriter(path=tmp_results_path)


# %% - Dataframes


@pytest.fixture(scope="session")
def inputs(inputs_reader: datasets.ParquetReader) -> schemas.Inputs:
    """Return the inputs data."""
    data = inputs_reader.read()
    return schemas.InputsSchema.check(data)


@pytest.fixture(scope="session")
def targets(targets_reader: datasets.ParquetReader) -> schemas.Targets:
    """Return the targets data."""
    data = targets_reader.read()
    return schemas.TargetsSchema.check(data)


@pytest.fixture(scope="session")
def outputs(outputs_reader: datasets.ParquetReader) -> schemas.Outputs:
    """Return the outputs data."""
    data = outputs_reader.read()
    return schemas.OutputsSchema.check(data)


# %% - Splitters


@pytest.fixture(scope="session")
def train_test_splitter() -> splitters.TrainTestSplitter:
    """Return the default train test splitter."""
    return splitters.TrainTestSplitter(test_size=TEST_SIZE)


@pytest.fixture(scope="session")
def time_series_splitter() -> splitters.TimeSeriesSplitter:
    """Return the default time series splitter."""
    return splitters.TimeSeriesSplitter(n_splits=N_SPLITS, test_size=TEST_SIZE)


@pytest.fixture(scope="session")
def train_test_split(
    train_test_splitter: splitters.TrainTestSplitter, inputs: schemas.Inputs, targets: schemas.Targets
) -> splitters.TrainTest:
    """Return the train and test indexes for the inputs dataframe."""
    return next(train_test_splitter.split(inputs=inputs, targets=targets))


@pytest.fixture(scope="session")
def train_test_sets(
    train_test_split: splitters.TrainTest, inputs: schemas.Inputs, targets: schemas.Targets
) -> tuple[schemas.Inputs, schemas.Targets, schemas.Inputs, schemas.Targets]:
    """Return the inputs/targets train and test sets from the train and test split."""
    train_index, test_index = train_test_split
    inputs_train, inputs_test = inputs.iloc[train_index], inputs.iloc[test_index]
    targets_train, targets_test = targets.iloc[train_index], targets.iloc[test_index]
    return inputs_train, targets_train, inputs_test, targets_test


# %% - Models


@pytest.fixture(scope="session")
def empty_model() -> models.BaselineSklearnModel:
    """Return an empty model for testing."""
    return models.BaselineSklearnModel()


@pytest.fixture(scope="session")
def default_model(
    empty_model: models.BaselineSklearnModel, inputs: schemas.Inputs, targets: schemas.Targets
) -> models.BaselineSklearnModel:
    """Return the default model."""
    model = empty_model.fit(inputs=inputs, targets=targets)
    # model.predict(inputs=inputs).to_parquet("tests/data/outputs.parquet")
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


# %% Serializers


@pytest.fixture(scope="function")
def model_serializer(tmp_model_path: str) -> serializers.JoblibModelSerializer:
    """Return the default model serializer."""
    return serializers.JoblibModelSerializer(path=tmp_model_path)


@pytest.fixture(scope="function")
def model_deserializer(
    default_model: models.Model, model_serializer: serializers.JoblibModelSerializer
) -> serializers.JoblibModelDeserializer:
    """Return the default model deserializer."""
    model_serializer.save(model=default_model)  # refresh model
    return serializers.JoblibModelDeserializer(path=model_serializer.path)


# %% - Resolvers


@pytest.fixture(scope="function", autouse=True)
def tmp_path_resolver(tmp_path: str) -> str:
    """Register tmp_path with Omegaconf."""

    def tmp_path_resolver() -> str:
        """Return tmp_path."""
        return tmp_path

    omegaconf.OmegaConf.register_new_resolver("tmp_path", tmp_path_resolver, replace=True)
    return tmp_path
