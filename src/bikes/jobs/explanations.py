"""Define a job for explaining the model structure and decisions."""

# %% IMPORTS

import typing as T

import pydantic as pdt

from bikes.core import schemas
from bikes.io import datasets, registries
from bikes.jobs import base

# %% JOBS


class ExplanationsJob(base.Job):
    """Generate explanations from the model and a data sample.

    Parameters:
        inputs_samples (datasets.ReaderKind): reader for the samples data.
        models_explanations (datasets.WriterKind): writer for models explanation.
        samples_explanations (datasets.WriterKind): writer for samples explanation.
        alias_or_version (str | int): alias or version for the  model.
        loader (registries.LoaderKind): registry loader for the model.
    """

    KIND: T.Literal["ExplanationsJob"] = "ExplanationsJob"

    # Samples
    inputs_samples: datasets.ReaderKind = pdt.Field(..., discriminator="KIND")
    # Explanations
    models_explanations: datasets.WriterKind = pdt.Field(..., discriminator="KIND")
    samples_explanations: datasets.WriterKind = pdt.Field(..., discriminator="KIND")
    # Model
    alias_or_version: str | int = "Champion"
    # Loader
    loader: registries.LoaderKind = pdt.Field(registries.CustomLoader(), discriminator="KIND")

    @T.override
    def run(self) -> base.Locals:
        # services
        logger = self.logger_service.logger()
        logger.info("With logger: {}", logger)
        # inputs
        logger.info("Read samples: {}", self.inputs_samples)
        inputs_samples = self.inputs_samples.read()  # unchecked!
        inputs_samples = schemas.InputsSchema.check(inputs_samples)
        logger.debug("- Inputs samples shape: {}", inputs_samples.shape)
        # model
        logger.info("With model: {}", self.mlflow_service.registry_name)
        model_uri = registries.uri_for_model_alias_or_version(
            name=self.mlflow_service.registry_name, alias_or_version=self.alias_or_version
        )
        logger.debug("- Model URI: {}", model_uri)
        # loader
        logger.info("Load model: {}", self.loader)
        model = self.loader.load(uri=model_uri).model.unwrap_python_model().model
        logger.debug("- Model: {}", model)
        # explanations
        # - models
        logger.info("Explain model: {}", model)
        models_explanations = model.explain_model()
        logger.debug("- Models explanations shape: {}", models_explanations.shape)
        # - samples
        logger.info("Explain samples: {}", len(inputs_samples))
        samples_explanations = model.explain_samples(inputs=inputs_samples)
        logger.debug("- Samples explanations shape: {}", samples_explanations.shape)
        # write
        # - model
        logger.info("Write models explanations: {}", self.models_explanations)
        self.models_explanations.write(data=models_explanations)
        # - samples
        logger.info("Write samples explanations: {}", self.samples_explanations)
        self.samples_explanations.write(data=samples_explanations)
        # notify
        self.alerts_service.notify(
            title="Explanations Job Finished", message=f"Features Count: {len(models_explanations)}"
        )
        return locals()
