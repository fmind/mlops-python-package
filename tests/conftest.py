"""Configuration for the tests."""

# %% IMPORTS

import os
import typing as T

import mlflow
import omegaconf
import pytest
from bikes import datasets, metrics, models, registers, schemas, searchers, services, splitters

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
def tmp_carbon_path(tmp_path: str) -> str:
    """Return a tmp path of the carbon folder."""
    return os.path.join(tmp_path, "carbons")


@pytest.fixture(scope="function")
def tmp_outputs_path(tmp_path: str) -> str:
    """Return a tmp path for the outputs dataset."""
    return os.path.join(tmp_path, "outputs.parquet")


@pytest.fixture(scope="function")
def tmp_results_path(tmp_path: str) -> str:
    """Return a tmp path of the results dataset."""
    return os.path.join(tmp_path, "results.parquet")


# %% - Configs


@pytest.fixture(scope="session")
def extra_config() -> str:
    """Extra config for scripts."""
    # use OmegaConf resolver for ${tmp_path:}
    string = """
    {
        "job": {
            "mlflow_service": {
                "tracking_uri": "${tmp_path:}/experiments/",
                "registry_uri": "${tmp_path:}/models/",
            }
        }
    }
    """
    return string


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
    train_test_splitter: splitters.TrainTestSplitter,
    inputs: schemas.Inputs,
    targets: schemas.Targets,
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
    return (
        T.cast(schemas.Inputs, inputs_train),
        T.cast(schemas.Targets, targets_train),
        T.cast(schemas.Inputs, inputs_test),
        T.cast(schemas.Targets, targets_test),
    )


# %% - Searchers


@pytest.fixture(scope="session")
def default_searcher() -> searchers.GridCVSearcher:
    """Return the default searcher."""
    param_grid = {"max_depth": [2, 4], "n_estimators": [10, 15]}
    return searchers.GridCVSearcher(param_grid=param_grid)


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
def logger_service() -> services.LoggerService:
    """Return and start the logger service."""
    service = services.LoggerService(colorize=False, diagnose=True)
    service.start()  # ready to be used
    return service


@pytest.fixture(scope="function")
def carbon_service(tmp_carbon_path: str) -> T.Generator[services.CarbonService, None, None]:
    """Return and start the carbon service."""
    service = services.CarbonService(output_dir=tmp_carbon_path)
    service.start()  # ready to be used
    yield service
    service.stop()


@pytest.fixture(scope="function", autouse=True)
def mlflow_service(tmp_path: str) -> services.MLflowService:
    """Return and start the mlflow service."""
    tracking_uri = f"{tmp_path}/experiments/"
    registry_uri = f"{tmp_path}/models/"
    service = services.MLflowService(
        tracking_uri=tracking_uri,
        registry_uri=registry_uri,
        experiment_name="Testing",
        registry_name="Testing",
    )
    service.start()  # ready to be used
    return service


# %% - Registers


@pytest.fixture(scope="session")
def default_signer() -> registers.InferSigner:
    """Return the default infer signer."""
    return registers.InferSigner()


@pytest.fixture(scope="session")
def default_signature(
    default_signer: registers.InferSigner, inputs: schemas.Inputs, outputs: schemas.Outputs
) -> registers.Signature:
    """Return the default signature."""
    return default_signer.sign(inputs=inputs, outputs=outputs)


@pytest.fixture(scope="session")
def default_saver() -> registers.CustomSaver:
    """Return the default model saver."""
    return registers.CustomSaver(path="test")


@pytest.fixture(scope="session")
def default_loader() -> registers.CustomLoader:
    """Return the default model loader."""
    return registers.CustomLoader()


# %% - Resolvers


@pytest.fixture(scope="session", autouse=True)
def test_data_path_resolver(data_path: str) -> str:
    """Register test_data with OmegaConf."""

    def test_data_resolver() -> str:
        """Get data_path."""
        return data_path

    omegaconf.OmegaConf.register_new_resolver(
        "test_data_path", test_data_resolver, use_cache=True, replace=True
    )
    return data_path


@pytest.fixture(scope="function", autouse=True)
def tmp_path_resolver(tmp_path: str) -> str:
    """Register tmp_path with Omegaconf."""

    def tmp_path_resolver() -> str:
        """Return tmp_path."""
        return tmp_path

    omegaconf.OmegaConf.register_new_resolver("tmp_path", tmp_path_resolver, replace=True)
    return tmp_path


# %% - Mlflow Registry


@pytest.fixture(scope="function")
def default_alias() -> str:
    """Return the default model alias."""
    return "Default"


@pytest.fixture(scope="function")
def default_mlflow_model_version(
    inputs: schemas.Inputs,
    default_alias: str,
    default_model: models.Model,
    default_saver: registers.CustomSaver,
    default_signature: registers.Signature,
    mlflow_service: services.MLflowService,
) -> registers.Version:
    """Return an MLflow version for the default model."""
    with mlflow.start_run(run_name="Default") as run:
        default_saver.save(model=default_model, signature=default_signature, input_example=inputs)
        version = mlflow_service.register(
            run_id=run.info.run_id, path=default_saver.path, alias=default_alias
        )
    return version
