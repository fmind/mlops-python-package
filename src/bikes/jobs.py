"""High-level jobs for the project."""

# %% IMPORTS

import abc
import typing as T

import pydantic as pdt
from loguru import logger

from bikes import datasets, metrics, models, schemas, searchers, serializers, services, splitters

# %% TYPES

# local job variables
Locals = dict[str, T.Any]

# %% JOBS


class Job(abc.ABC, pdt.BaseModel, strict=True):
    """Base class for a job.

    use a job to execute runs in  context.
    e.g., to define common services like logger

    Attributes:
        logger_service: manage the logging system.
    """

    KIND: str

    # services
    logger_service: services.Service = services.LoggerService()

    def __enter__(self) -> T.Self:
        """Enter the job context.

        Returns:
            T.Self: return the current object.
        """
        # services
        self.logger_service.start()
        # return
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
        # services
        self.logger_service.stop()
        # return
        return False  # do not suppress exceptions

    @abc.abstractmethod
    def run(self) -> Locals:
        """Run the job in context.

        Returns:
            Locals: local job variables.
        """


class TuningJob(Job):
    """Find the best hyperparameters for a model.

    Attributes:
        inputs: dataset reader with inputs variables.
        targets: dataset reader with targets variables.
        results: dataset writer for searcher results.
        model: machine learning model to tune.
        metric: main metric for evaluation.
        splitter: splitter for datasets.
        searcher: searcher algorithm.
    """

    KIND: T.Literal["TuningJob"] = "TuningJob"

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
        logger.info("Run searcher: {}", self.searcher)
        results, best_score, best_params = self.searcher.search(
            model=self.model, metric=self.metric, cv=self.splitter, inputs=inputs, targets=targets
        )
        logger.info("- Results: {}", len(results))
        logger.info("- Best Score: {}", best_score)
        logger.info("- Best Params: {}", best_params)
        # write
        logger.info("Write results: {}", self.results)
        self.results.write(results)
        return locals()


class TrainingJob(Job):
    """Train and register a single AI/ML model

    Attributes:
        inputs: dataset reader with inputs variables.
        targets: dataset reader with targets variables.
        serializer: serializer for the trained model.
        model: machine learning model to tune.
        scorers: metrics for the evaluation.
        splitter: splitter for datasets.
    """

    KIND: T.Literal["TrainingJob"] = "TrainingJob"

    # read
    inputs: datasets.ReaderKind
    targets: datasets.ReaderKind
    # write
    serializer: serializers.ModelSerializerKind
    # model
    model: models.ModelKind = models.BaselineSklearnModel()
    # scorers
    scorers: list[metrics.MetricKind] = [metrics.SklearnMetric()]
    # splitter
    splitter: splitters.SplitterKind = splitters.TrainTestSplitter()

    @T.override
    def run(self) -> Locals:
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
        assert len(inputs_train) == len(targets_train), "Inputs and targets train should have the same length!"
        assert len(inputs_test) == len(targets_test), "Inputs and targets test should have the same length!"
        # model
        logger.info("Fit model: {}", self.model)
        self.model.fit(inputs=inputs_train, targets=targets_train)
        # outputs
        logger.info("Predict outputs: {}", len(inputs_test))
        outputs_test = self.model.predict(inputs=inputs_test)
        logger.info("- Outputs test shape: {}", outputs_test.shape)
        assert len(inputs_test) == len(outputs_test), "Inputs and outputs test should have the same length!"
        # metric
        for i, scorer in enumerate(self.scorers, start=1):
            logger.info("{}. Run scorer: {}", i, scorer)
            score = scorer.score(targets=targets_test, outputs=outputs_test)
            logger.info("- Metric score: {}", score)
        # write
        logger.info("Write model: {}", self.serializer)
        self.serializer.save(model=self.model)
        return locals()


class InferenceJob(Job):
    """Load a model and generate predictions.

    Attributes:
        inputs: dataset reader with inputs variables.
        outputs: dataset writer for the model outputs.
        deserializer: deserializer for the trained model.
    """

    KIND: T.Literal["InferenceJob"] = "InferenceJob"

    # inputs
    inputs: datasets.ReaderKind
    # outputs
    outputs: datasets.WriterKind
    # model
    deserializer: serializers.ModelDeserializerKind

    @T.override
    def run(self) -> Locals:
        # inputs
        logger.info("Read inputs: {}", self.inputs)
        inputs = self.inputs.read()
        inputs = schemas.InputsSchema.check(inputs)
        logger.info("- Inputs shape: {}", inputs.shape)
        # model
        logger.info("With deserializer: {}", self.deserializer)
        model = self.deserializer.load()
        logger.info("- Model loaded: {}", model)
        # predict
        logger.info("Predict outputs: {}", len(inputs))
        outputs = model.predict(inputs=inputs)
        logger.info("- Outputs shape: {}", outputs.shape)
        assert len(inputs) == len(outputs), "Inputs and outputs should have the same length!"
        # outputs
        logger.info("Write outputs: {}", self.outputs)
        self.outputs.write(data=outputs)
        return locals()


JobKind = TuningJob | TrainingJob | InferenceJob
