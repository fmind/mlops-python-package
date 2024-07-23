"""Define a job for generating batch predictions from a registered model."""

# %% IMPORTS

import typing as T

import pydantic as pdt

from bikes.core import schemas
from bikes.io import datasets, registries
from bikes.jobs import base

# %% JOBS


class InferenceJob(base.Job):
    """Generate batch predictions from a registered model.

    Parameters:
        inputs (datasets.ReaderKind): reader for the inputs data.
        outputs (datasets.WriterKind): writer for the outputs data.
        alias_or_version (str | int): alias or version for the  model.
        loader (registries.LoaderKind): registry loader for the model.
    """

    KIND: T.Literal["InferenceJob"] = "InferenceJob"

    # Inputs
    inputs: datasets.ReaderKind = pdt.Field(..., discriminator="KIND")
    # Outputs
    outputs: datasets.WriterKind = pdt.Field(..., discriminator="KIND")
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
        logger.info("Read inputs: {}", self.inputs)
        inputs_ = self.inputs.read()  # unchecked!
        inputs = schemas.InputsSchema.check(inputs_)
        logger.debug("- Inputs shape: {}", inputs.shape)
        # model
        logger.info("With model: {}", self.mlflow_service.registry_name)
        model_uri = registries.uri_for_model_alias_or_version(
            name=self.mlflow_service.registry_name, alias_or_version=self.alias_or_version
        )
        logger.debug("- Model URI: {}", model_uri)
        # loader
        logger.info("Load model: {}", self.loader)
        model = self.loader.load(uri=model_uri)
        logger.debug("- Model: {}", model)
        # outputs
        logger.info("Predict outputs: {}", len(inputs))
        outputs = model.predict(inputs=inputs)  # checked
        logger.debug("- Outputs shape: {}", outputs.shape)
        # write
        logger.info("Write outputs: {}", self.outputs)
        self.outputs.write(data=outputs)
        # notify
        self.alerts_service.notify(
            title="Inference Job Finished", message=f"Outputs Shape: {outputs.shape}"
        )
        return locals()
