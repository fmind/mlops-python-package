"""Connect candidate selection to evaluation and promotion of one model version."""

import typing as T

from bikes.jobs import base
from bikes.jobs.evaluations import EvaluationsJob
from bikes.jobs.explanations import ExplanationsJob
from bikes.jobs.inference import InferenceJob
from bikes.jobs.promotion import PromotionJob
from bikes.jobs.training import TrainingJob
from bikes.jobs.tuning import TuningJob


class PipelineJob(base.Job):
    """Tune, train, evaluate and promote one candidate, then run optional consumers.

    Child jobs share this job's services. Evaluation failures propagate before the
    alias changes. All consumers use the immutable version returned by training.
    """

    KIND: T.Literal["PipelineJob"] = "PipelineJob"
    tuning: TuningJob
    training: TrainingJob
    evaluations: EvaluationsJob
    alias: str = "Champion"
    inference: InferenceJob | None = None
    explanations: ExplanationsJob | None = None

    def _configured(self, job: base.Job, **updates: T.Any) -> base.Job:
        """Validate a stage with shared services and explicit candidate overrides."""
        config = (
            job.model_dump()
            | {
                "logger_service": self.logger_service,
                "alerts_service": self.alerts_service,
                "mlflow_service": self.mlflow_service,
            }
            | updates
        )
        return type(job).model_validate(config)

    @T.override
    def run(self) -> base.Locals:
        """Run every stage; failed validation leaves the current alias unchanged."""
        tuning = self._configured(self.tuning).run()
        selected = type(self.tuning.model).model_validate(self.tuning.model.model_dump() | tuning["best_params"])
        run_config = self.training.run_config.model_dump()
        run_config["tags"] = (run_config.get("tags") or {}) | {
            "tuning_run_id": tuning["run"].info.run_id,
        }
        training = self._configured(self.training, model=selected, run_config=run_config).run()
        version = int(training["model_version"].version)
        evaluations = self._configured(self.evaluations, alias_or_version=version).run()
        promotion = PromotionJob(
            logger_service=self.logger_service,
            alerts_service=self.alerts_service,
            mlflow_service=self.mlflow_service,
            version=version,
            alias=self.alias,
        ).run()
        inference = self._configured(self.inference, alias_or_version=version).run() if self.inference else None
        explanations = (
            self._configured(self.explanations, alias_or_version=version).run() if self.explanations else None
        )
        return locals()
