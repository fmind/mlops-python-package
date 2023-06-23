"""High-level jobs for the project."""

# %% IMPORTS

import abc
import typing as T

import pydantic as pdt
from loguru import logger

from wines import datasets, metrics, models, schemas, searchers, services, splitters

# %% TYPINGS

# local job variables
Locals = T.Dict[str, T.Any]

# %% JOBS


class Job(abc.ABC, pdt.BaseModel):
    """Base class for a job."""

    # note: use jobs to provide run contexts
    # e.g., to define common services like logger

    KIND: str

    # services
    logger_service: services.Service = services.LoggerService()

    def __enter__(self) -> "Job":
        """Enter the context."""
        # services
        self.logger_service.start()
        # return
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> T.Literal[False]:
        """Exit the context."""
        # exceptions
        if exc_type is not None:
            logger.exception(f'EXCEPTION IN JOB: "{self.KIND}" ({exc_type}): {exc_value}')
        # services
        self.logger_service.stop()
        # return
        return False  # do not suppress exceptions

    @abc.abstractmethod
    def run(self) -> Locals:
        """Run the job in context."""


class TuningJob(Job):
    """Find the best hyperparameters for a model."""

    KIND: T.Literal["TuningJob"] = "TuningJob"

    # data
    inputs: datasets.DatasetKind
    target: datasets.DatasetKind
    # model
    model: models.ModelKind = models.BaselineSklearnModel()
    # metric
    metric: metrics.MetricKind = metrics.SklearnMetric()
    # searcher
    searcher: searchers.SearcherKind = searchers.GridCVSearcher(
        param_grid={"max_depth": [3, 5, 7]},
    )
    # outputs
    output_results: T.Optional[str] = None

    def run(self) -> Locals:
        """Run the tuning job in context."""
        # data
        # - inputs
        logger.info("Read inputs: %s", self.inputs)
        inputs = self.inputs.read()
        inputs = schemas.InputsSchema.check(inputs)
        logger.info("- Inputs shape: %s", inputs.shape)
        # - target
        logger.info("Read target: {}", self.target)
        target = self.target.read()
        target = schemas.TargetSchema.check(target)
        logger.info("- Target shape: {}", target.shape)
        # model
        logger.info("With model: {}", self.model)
        # metric
        logger.info("With metric: {}", self.metric)
        # searcher
        logger.info("Run searcher: {}", self.searcher)
        results, best_params, best_score = self.searcher.search(
            model=self.model, metric=self.metric, inputs=inputs, target=target
        )
        logger.info("- Results: {}", len(results))
        logger.info("- Best Score: {}", best_score)
        logger.info("- Best Params: {}", best_params)
        # outputs
        if self.output_results is not None:
            logger.info("Save results to: {}", self.output_results)
            self.searcher.save(path=self.output_results)
        return locals()


class TrainingJob(Job):
    """Train and register a single AI/ML model"""

    KIND: T.Literal["TrainingJob"] = "TrainingJob"

    # data
    inputs: datasets.DatasetKind
    target: datasets.DatasetKind
    # model
    model: models.ModelKind = models.BaselineSklearnModel()
    # metric
    metric: metrics.MetricKind = metrics.SklearnMetric()
    # splitter
    splitter: splitters.SplitterKind = splitters.TrainTestSplitter()
    # outputs
    output_model: T.Optional[str] = None

    def run(self) -> Locals:
        """Run the training job in context."""
        # data
        # - inputs
        logger.info("Read inputs: {}", self.inputs)
        inputs = self.inputs.read()
        logger.info("- Inputs shape: {}", inputs.shape)
        logger.info("- With splitter: {}", self.splitter)
        inputs_train, inputs_test = [schemas.InputsSchema.check(split) for split in self.splitter.split(inputs)]
        logger.info("- Inputs train shape: {}", inputs_train.shape)
        logger.info("- Inputs test shape: {}", inputs_test.shape)
        # - target
        logger.info("Read target: {}", self.target)
        target = self.target.read()
        logger.info("- Target shape: {}", target.shape)
        logger.info("- With splitter: {}", self.splitter)
        target_train, target_test = [schemas.TargetSchema.check(split) for split in self.splitter.split(target)]
        logger.info("- Target train shape: {}", target_train.shape)
        logger.info("- Target test shape: {}", target_test.shape)
        # model
        logger.info("Fit model: {}", self.model)
        self.model.fit(inputs=inputs_train, target=target_train)
        # output
        logger.info("Predict output: {}", len(inputs_test))
        output_test = self.model.predict(inputs=inputs_test)
        logger.info("- Output test shape: {}", output_test.shape)
        # metric
        logger.info("Compute score with metric: {}", self.metric)
        score = self.metric.score(target=target_test, output=output_test)
        logger.info("- Metric score: {}", score)
        # outputs
        if self.output_model is not None:
            logger.info("Write model to: {}", self.output_model)
            self.model.save(path=self.output_model)
        return locals()


class InferenceJob(Job):
    """Load a model and generate predictions."""

    KIND: T.Literal["InferenceJob"] = "InferenceJob"

    # inputs
    inputs: datasets.DatasetKind
    # model
    model_path: str
    # output
    output: datasets.DatasetKind

    def run(self) -> Locals:
        """Run the inference job in context."""
        # inputs
        logger.info("Read inputs: {}", self.inputs)
        inputs = self.inputs.read()
        inputs = schemas.InputsSchema.check(inputs)
        logger.info("- Inputs shape: {}", inputs.shape)
        # model
        logger.info("Load model: {}", self.model_path)
        model = models.Model.load(path=self.model_path)
        logger.info("- Model loaded: {}", model)
        # predict
        logger.info("Predict output: {}", len(inputs))
        output = model.predict(inputs=inputs)
        logger.info("- Output shape: {}", output.shape)
        # output
        logger.info("Write output: {}", self.output)
        self.output.write(data=output)
        return locals()


# alias to all job kinds
JobKind = T.Union[TuningJob, TrainingJob, InferenceJob]
