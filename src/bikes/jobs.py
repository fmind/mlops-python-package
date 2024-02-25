"""High-level jobs for the project."""

# %% IMPORTS

import abc
import typing as T

import mlflow
import pydantic as pdt
from loguru import logger

from bikes import datasets, metrics, models, registers, schemas, searchers, services, splitters

# %% TYPES

# local job variables
Locals = dict[str, T.Any]

# %% JOBS


class Job(abc.ABC, pdt.BaseModel, strict=True):
    """Base class for a job.

    use a job to execute runs in  context.
    e.g., to define common services like logger

    Attributes:
        logger_service (services.LoggerService): manage the logging system.
        mlflow_service (services.MLflowService): manage the mlflow system.
    """

    KIND: str

    logger_service: services.LoggerService = services.LoggerService()
    mlflow_service: services.MLflowService = services.MLflowService()

    def __enter__(self) -> T.Self:
        """Enter the job context.

        Returns:
            T.Self: return the current object.
        """
        self.logger_service.start()
        logger.debug("[START] MLflow service: {}", self.mlflow_service)
        self.mlflow_service.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> T.Literal[False]:
        """Exit the job context.

        Args:
            exc_type: ignored.
            exc_value: ignored.
            traceback: ignored.

        Returns:
            T.Literal[False]: always propagate exceptions.
        """
        logger.debug("[STOP] MLflow service: {}", self.mlflow_service)
        self.mlflow_service.stop()
        self.logger_service.stop()
        return False

    @abc.abstractmethod
    def run(self) -> Locals:
        """Run the job in context.

        Returns:
            Locals: local job variables.
        """


class TuningJob(Job):
    """Find the best hyperparameters for a model.

    Attributes:
        run_name (str): name of the MLflow experiment run.
        inputs (datasets.ReaderKind): dataset reader with inputs variables.
        targets (datasets.ReaderKind): dataset reader with targets variables.
        results (datasets.WriterKind): dataset writer for searcher results.
        model (models.ModelKind): machine learning model to tune.
        metric (metrics.MetricKind): main metric for evaluation.
        splitter (splitters.SplitterKind): splitter for datasets.
        searcher (searchers.SearcherKind): searcher algorithm.
    """

    KIND: T.Literal["TuningJob"] = "TuningJob"

    # run
    run_name: str = "Tuning"
    # read
    inputs: datasets.ReaderKind
    targets: datasets.ReaderKind
    # write
    results: datasets.WriterKind
    # model
    model: models.ModelKind = models.BaselineSklearnModel()
    # metric
    metric: metrics.MetricKind = metrics.SklearnMetric()
    # splitter
    splitter: splitters.SplitterKind = splitters.TimeSeriesSplitter()
    # searcher
    searcher: searchers.SearcherKind = searchers.GridCVSearcher(
        param_grid={"max_depth": [3, 5, 7]},
    )

    @T.override
    def run(self) -> Locals:
        # run
        logger.info("Start run: {} ", self.run_name)
        with mlflow.start_run(run_name=self.run_name) as run:
            logger.info("- Run ID: {}", run.info.run_id)
            # read
            # - inputs
            logger.info("Read inputs: {}", self.inputs)
            inputs = schemas.InputsSchema.check(self.inputs.read())
            logger.info("- Inputs shape: {}", inputs.shape)
            # - targets
            logger.info("Read targets: {}", self.targets)
            targets = schemas.TargetsSchema.check(self.targets.read())
            logger.info("- Targets shape: {}", targets.shape)
            # - asserts
            assert len(inputs) == len(targets), "Inputs and targets should have the same length!"
            # model
            logger.info("With model: {}", self.model)
            # metric
            logger.info("With metric: {}", self.metric)
            # splitter
            logger.info("With splitter: {}", self.splitter)
            # searcher
            logger.info("Execute searcher: {}", self.searcher)
            results, best_score, best_params = self.searcher.search(
                model=self.model,
                metric=self.metric,
                cv=self.splitter,
                inputs=inputs,
                targets=targets,
            )
            logger.info("- # Results: {}", len(results))
            logger.info("- Best Score: {}", best_score)
            logger.info("- Best Params: {}", best_params)
            # write
            logger.info("Write results: {}", self.results)
            self.results.write(results)
        return locals()


class TrainingJob(Job):
    """Train and register a single AI/ML model.

    Attributes:
        run_name (str): name of the MLflow experiment run.
        inputs (datasets.ReaderKind): dataset reader with inputs variables.
        targets (datasets.ReaderKind): dataset reader with targets variables.
        saver (registers.SaverKind): save the trained model in registry.
        model (models.ModelKind): machine learning model to tune.
        signer (registers.SignerKind): signer for the trained model.
        scorers (list[metrics.MetricKind]): metrics for the evaluation.
        splitter (splitters.SplitterKind): splitter for datasets.
        registry_alias (str): alias of model.
    """

    KIND: T.Literal["TrainingJob"] = "TrainingJob"

    # run
    run_name: str = "Training"
    # read
    inputs: datasets.ReaderKind
    targets: datasets.ReaderKind
    # write
    saver: registers.SaverKind = registers.CustomSaver()
    # model
    model: models.ModelKind = models.BaselineSklearnModel()
    # signer
    signer: registers.SignerKind = registers.InferSigner()
    # scorers
    scorers: list[metrics.MetricKind] = [metrics.SklearnMetric()]
    # splitter
    splitter: splitters.SplitterKind = splitters.TrainTestSplitter()
    # register
    registry_alias: str = "Champion"

    @T.override
    def run(self) -> Locals:
        # run
        logger.info("Start run: {} ", self.run_name)
        with mlflow.start_run(run_name=self.run_name) as run:
            logger.info("- Run ID: {}", run.info.run_id)
            # read
            # - inputs
            logger.info("Read inputs: {}", self.inputs)
            inputs = schemas.InputsSchema.check(self.inputs.read())
            logger.info("- Inputs shape: {}", inputs.shape)
            # - targets
            logger.info("Read targets: {}", self.targets)
            targets = schemas.TargetsSchema.check(self.targets.read())
            logger.info("- Targets shape: {}", targets.shape)
            # - asserts
            assert len(inputs) == len(targets), "Inputs and targets should have the same length!"
            # split
            logger.info("With splitter: {}", self.splitter)
            # - index
            train_index, test_index = next(self.splitter.split(inputs=inputs, targets=targets))
            # - inputs
            inputs_train, inputs_test = inputs.iloc[train_index], inputs.iloc[test_index]
            logger.info("- Inputs train shape: {}", inputs_train.shape)
            logger.info("- Inputs test shape: {}", inputs_test.shape)
            # - targets
            targets_train, targets_test = targets.iloc[train_index], targets.iloc[test_index]
            logger.info("- Targets train shape: {}", targets_train.shape)
            logger.info("- Targets test shape: {}", targets_test.shape)
            # - asserts
            assert len(inputs_train) == len(
                targets_train
            ), "Inputs and targets train should have the same length!"
            assert len(inputs_test) == len(
                targets_test
            ), "Inputs and targets test should have the same length!"
            # model
            logger.info("Fit model: {}", self.model)
            self.model.fit(inputs=inputs_train, targets=targets_train)
            # outputs
            logger.info("Predict outputs: {}", len(inputs_test))
            outputs_test = self.model.predict(inputs=inputs_test)
            logger.info("- Outputs test shape: {}", outputs_test.shape)
            assert len(inputs_test) == len(
                outputs_test
            ), "Inputs and outputs test should have the same length!"
            # scorers
            for i, scorer in enumerate(self.scorers, start=1):
                logger.info("{}. Run scorer: {}", i, scorer)
                score = scorer.score(targets=targets_test, outputs=outputs_test)
                mlflow.log_metric(key=scorer.name, value=score)
                logger.info("- Metric score: {}", score)
            # sign
            logger.info("Sign model: {}", self.signer)
            signature = self.signer.sign(inputs=inputs, outputs=outputs_test)
            logger.info("- Model signature: {}", signature.to_dict())
            # save
            logger.info("Save model: {}", self.saver)
            info = self.saver.save(model=self.model, signature=signature, input_example=inputs)
            logger.info("- Model URI: {}", info.model_uri)
            # register
            logger.info("Register model: {}", self.registry_alias)
            version = self.mlflow_service.register(
                run_id=run.info.run_id, path=self.saver.path, alias=self.registry_alias
            )
            logger.info("- Model version: {}", version.version)
        return locals()


class InferenceJob(Job):
    """Load a model and generate predictions.

    Attributes:
        inputs (datasets.ReaderKind): dataset reader with inputs variables.
        outputs (datasets.WriterKind): dataset writer for the model outputs.
        registry_alias (str): alias of the model to load.
        loader (registers.LoaderKind): load the model from registry.
    """

    KIND: T.Literal["InferenceJob"] = "InferenceJob"

    # data
    inputs: datasets.ReaderKind
    outputs: datasets.WriterKind
    # model
    registry_alias: str = "Champion"
    loader: registers.LoaderKind = registers.CustomLoader()

    @T.override
    def run(self) -> Locals:
        # read
        logger.info("Read inputs: {}", self.inputs)
        inputs = self.inputs.read()
        inputs = schemas.InputsSchema.check(inputs)
        logger.info("- Inputs shape: {}", inputs.shape)
        # uri
        uri = f"models:/{self.mlflow_service.registry_name}@{self.registry_alias}"
        logger.info("With URI: {}", uri)
        # load
        logger.info("Load model: {}", self.loader)
        model = self.loader.load(uri=uri)
        logger.info("- Model: {}", model)
        # predict
        logger.info("Predict outputs: {}", len(inputs))
        outputs = model.predict(data=inputs)
        logger.info("- Outputs shape: {}", outputs.shape)
        # write
        logger.info("Write outputs: {}", self.outputs)
        self.outputs.write(data=outputs)
        return locals()


JobKind = TuningJob | TrainingJob | InferenceJob
