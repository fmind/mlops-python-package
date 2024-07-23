"""Define a job for training and registring a single AI/ML model."""

# %% IMPORTS

import typing as T

import mlflow
import pydantic as pdt

from bikes.core import metrics as metrics_
from bikes.core import models, schemas
from bikes.io import datasets, registries, services
from bikes.jobs import base
from bikes.utils import signers, splitters

# %% JOBS


class TrainingJob(base.Job):
    """Train and register a single AI/ML model.

    Parameters:
        run_config (services.MlflowService.RunConfig): mlflow run config.
        inputs (datasets.ReaderKind): reader for the inputs data.
        targets (datasets.ReaderKind): reader for the targets data.
        model (models.ModelKind): machine learning model to train.
        metrics (metrics_.MetricKind): metrics for the reporting.
        splitter (splitters.SplitterKind): data sets splitter.
        saver (registries.SaverKind): model saver.
        signer (signers.SignerKind): model signer.
        registry (registries.RegisterKind): model register.
    """

    KIND: T.Literal["TrainingJob"] = "TrainingJob"

    # Run
    run_config: services.MlflowService.RunConfig = services.MlflowService.RunConfig(name="Training")
    # Data
    inputs: datasets.ReaderKind = pdt.Field(..., discriminator="KIND")
    targets: datasets.ReaderKind = pdt.Field(..., discriminator="KIND")
    # Model
    model: models.ModelKind = pdt.Field(models.BaselineSklearnModel(), discriminator="KIND")
    # Metrics
    metrics: list[metrics_.MetricKind] = pdt.Field([metrics_.SklearnMetric()], discriminator="KIND")
    # Splitter
    splitter: splitters.SplitterKind = pdt.Field(
        splitters.TrainTestSplitter(), discriminator="KIND"
    )
    # Saver
    saver: registries.SaverKind = pdt.Field(registries.CustomSaver(), discriminator="KIND")
    # Signer
    signer: signers.SignerKind = pdt.Field(signers.InferSigner(), discriminator="KIND")
    # Registrer
    # - avoid shadowing pydantic `register` pydantic function
    registry: registries.RegisterKind = pdt.Field(registries.MlflowRegister(), discriminator="KIND")

    @T.override
    def run(self) -> base.Locals:
        # services
        # - logger
        logger = self.logger_service.logger()
        logger.info("With logger: {}", logger)
        # - mlflow
        client = self.mlflow_service.client()
        logger.info("With client: {}", client.tracking_uri)
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
            # splitter
            logger.info("With splitter: {}", self.splitter)
            # - index
            train_index, test_index = next(self.splitter.split(inputs=inputs, targets=targets))
            # - inputs
            inputs_train = T.cast(schemas.Inputs, inputs.iloc[train_index])
            inputs_test = T.cast(schemas.Inputs, inputs.iloc[test_index])
            logger.debug("- Inputs train shape: {}", inputs_train.shape)
            logger.debug("- Inputs test shape: {}", inputs_test.shape)
            # - targets
            targets_train = T.cast(schemas.Targets, targets.iloc[train_index])
            targets_test = T.cast(schemas.Targets, targets.iloc[test_index])
            logger.debug("- Targets train shape: {}", targets_train.shape)
            logger.debug("- Targets test shape: {}", targets_test.shape)
            # model
            logger.info("Fit model: {}", self.model)
            self.model.fit(inputs=inputs_train, targets=targets_train)
            # outputs
            logger.info("Predict outputs: {}", len(inputs_test))
            outputs_test = self.model.predict(inputs=inputs_test)
            logger.debug("- Outputs test shape: {}", outputs_test.shape)
            # metrics
            for i, metric in enumerate(self.metrics, start=1):
                logger.info("{}. Compute metric: {}", i, metric)
                score = metric.score(targets=targets_test, outputs=outputs_test)
                client.log_metric(run_id=run.info.run_id, key=metric.name, value=score)
                logger.debug("- Metric score: {}", score)
            # signer
            logger.info("Sign model: {}", self.signer)
            model_signature = self.signer.sign(inputs=inputs, outputs=outputs_test)
            logger.debug("- Model signature: {}", model_signature.to_dict())
            # saver
            logger.info("Save model: {}", self.saver)
            model_info = self.saver.save(
                model=self.model, signature=model_signature, input_example=inputs
            )
            logger.debug("- Model URI: {}", model_info.model_uri)
            # register
            logger.info("Register model: {}", self.registry)
            model_version = self.registry.register(
                name=self.mlflow_service.registry_name, model_uri=model_info.model_uri
            )
            logger.debug("- Model version: {}", model_version)
            # notify
            self.alerts_service.notify(
                title="Training Job Finished", message=f"Model version: {model_version.version}"
            )
        return locals()
