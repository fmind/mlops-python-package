"""Define a job for finding the best hyperparameters for a model."""

# %% IMPORTS

import typing as T

import mlflow
import pydantic as pdt

from bikes.core import metrics, models, schemas
from bikes.io import datasets, services
from bikes.jobs import base
from bikes.utils import searchers, splitters

# %% JOBS


class TuningJob(base.Job):
    """Find the best hyperparameters for a model.

    Parameters:
        run_config (services.MlflowService.RunConfig): mlflow run config.
        inputs (datasets.ReaderKind): reader for the inputs data.
        targets (datasets.ReaderKind): reader for the targets data.
        model (models.ModelKind): machine learning model to tune.
        metric (metrics.MetricKind): tuning metric to optimize.
        splitter (splitters.SplitterKind): data sets splitter.
        searcher: (searchers.SearcherKind): hparams searcher.
    """

    KIND: T.Literal["TuningJob"] = "TuningJob"

    # Run
    run_config: services.MlflowService.RunConfig = services.MlflowService.RunConfig(name="Tuning")
    # Data
    inputs: datasets.ReaderKind = pdt.Field(..., discriminator="KIND")
    targets: datasets.ReaderKind = pdt.Field(..., discriminator="KIND")
    # Model
    model: models.ModelKind = pdt.Field(models.BaselineSklearnModel(), discriminator="KIND")
    # Metric
    metric: metrics.MetricKind = pdt.Field(metrics.SklearnMetric(), discriminator="KIND")
    # splitter
    splitter: splitters.SplitterKind = pdt.Field(
        splitters.TimeSeriesSplitter(), discriminator="KIND"
    )
    # Searcher
    searcher: searchers.SearcherKind = pdt.Field(
        searchers.GridCVSearcher(
            param_grid={
                "max_depth": [3, 5, 7],
            }
        ),
        discriminator="KIND",
    )

    @T.override
    def run(self) -> base.Locals:
        """Run the tuning job in context."""
        # services
        # - logger
        logger = self.logger_service.logger()
        logger.info("With logger: {}", logger)
        with self.mlflow_service.run_context(run_config=self.run_config) as run:
            logger.info("With run context: {}", run.info)
            # data
            # - inputs
            logger.info("Read inputs: {}", self.inputs)
            inputs_ = self.inputs.read()  # unchecked!
            inputs = schemas.InputsSchema.check(inputs_)
            logger.debug("- Inputs shape: {}", inputs.shape)
            # - targets
            logger.info("Read targets: {}", self.targets)
            targets_ = self.targets.read()  # unchecked!
            targets = schemas.TargetsSchema.check(targets_)
            logger.debug("- Targets shape: {}", targets.shape)
            # lineage
            # - inputs
            logger.info("Log lineage: inputs")
            inputs_lineage = self.inputs.lineage(data=inputs, name="inputs")
            mlflow.log_input(dataset=inputs_lineage, context=self.run_config.name)
            logger.debug("- Inputs lineage: {}", inputs_lineage.to_dict())
            # - targets
            logger.info("Log lineage: targets")
            targets_lineage = self.targets.lineage(
                data=targets, name="targets", targets=schemas.TargetsSchema.cnt
            )
            mlflow.log_input(dataset=targets_lineage, context=self.run_config.name)
            logger.debug("- Targets lineage: {}", targets_lineage.to_dict())
            # model
            logger.info("With model: {}", self.model)
            # metric
            logger.info("With metric: {}", self.metric)
            # splitter
            logger.info("With splitter: {}", self.splitter)
            # searcher
            logger.info("Run searcher: {}", self.searcher)
            results, best_score, best_params = self.searcher.search(
                model=self.model,
                metric=self.metric,
                inputs=inputs,
                targets=targets,
                cv=self.splitter,
            )
            logger.debug("- Results: {}", results.shape)
            logger.debug("- Best Score: {}", best_score)
            logger.debug("- Best Params: {}", best_params)
            # notify
            self.alerts_service.notify(
                title="Tuning Job Finished", message=f"Best score: {best_score}"
            )
        return locals()
