"""Define a job for promoting a registered model version with an alias."""

# %% IMPORTS

import typing as T

from bikes.jobs import base

# %% JOBS


class PromotionJob(base.Job):
    """Define a job for promoting a registered model version with an alias.

    https://mlflow.org/docs/latest/model-registry.html#concepts

    Parameters:
        alias (str): the mlflow alias to transition the registered model version.
        version (int | None): the model version to transition (use None for latest).
    """

    KIND: T.Literal["PromotionJob"] = "PromotionJob"

    alias: str = "Champion"
    version: int | None = None

    @T.override
    def run(self) -> base.Locals:
        # services
        # - logger
        logger = self.logger_service.logger()
        logger.info("With logger: {}", logger)
        # - mlflow
        client = self.mlflow_service.client()
        logger.info("With client: {}", client)
        name = self.mlflow_service.registry_name
        # version
        if self.version is None:  # use the latest model version
            version = client.search_model_versions(
                f"name='{name}'", max_results=1, order_by=["version_number DESC"]
            )[0].version
        else:
            version = self.version
        logger.info("From version: {}", version)
        # alias
        logger.info("To alias: {}", self.alias)
        # promote
        logger.info("Promote model: {}", name)
        client.set_registered_model_alias(name=name, alias=self.alias, version=version)
        model_version = client.get_model_version_by_alias(name=name, alias=self.alias)
        logger.debug("- Model version: {}", model_version)
        # notify
        self.alerts_service.notify(
            title="Promotion Job Finished",
            message=f"Version: {model_version.version} @ {self.alias}",
        )
        return locals()
