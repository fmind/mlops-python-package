"""High-level jobs of the project."""

# %% IMPORTS

from regression_model_template.jobs.evaluations import EvaluationsJob
from regression_model_template.jobs.explanations import ExplanationsJob
from regression_model_template.jobs.inference import InferenceJob
from regression_model_template.jobs.promotion import PromotionJob
from regression_model_template.jobs.training import TrainingJob
from regression_model_template.jobs.tuning import TuningJob

# %% TYPES

JobKind = TuningJob | TrainingJob | PromotionJob | InferenceJob | EvaluationsJob | ExplanationsJob

# %% EXPORTS

__all__ = [
    "TuningJob",
    "TrainingJob",
    "PromotionJob",
    "InferenceJob",
    "EvaluationsJob",
    "ExplanationsJob",
    "JobKind",
]
