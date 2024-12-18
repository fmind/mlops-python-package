"""High-level jobs of the project."""

# %% IMPORTS

from model_name.jobs.evaluations import EvaluationsJob
from model_name.jobs.explanations import ExplanationsJob
from model_name.jobs.inference import InferenceJob
from model_name.jobs.promotion import PromotionJob
from model_name.jobs.training import TrainingJob
from model_name.jobs.tuning import TuningJob

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
