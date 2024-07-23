"""High-level jobs of the project."""

# %% IMPORTS

from bikes.jobs.evaluations import EvaluationsJob
from bikes.jobs.explanations import ExplanationsJob
from bikes.jobs.inference import InferenceJob
from bikes.jobs.promotion import PromotionJob
from bikes.jobs.training import TrainingJob
from bikes.jobs.tuning import TuningJob

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
