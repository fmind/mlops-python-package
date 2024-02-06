"""Scripts for the Command-Line Interface (CLI)."""

# %% IMPORTS

import argparse

import pydantic as pdt
import pydantic_settings as pdts

from bikes import configs, jobs

# %% SETTINGS


class Settings(pdts.BaseSettings):
    """Settings for the program."""

    job: jobs.JobKind = pdt.Field(..., discriminator="KIND")


# %% PARSERS

parser = argparse.ArgumentParser(description="Run a job from configs.")
parser.add_argument("configs", nargs="+", help="Config files for a job.")

# %% SCRIPTS


def main() -> None:
    """Main entry point."""
    args = parser.parse_args()  # from sys.argv
    config = configs.load_configs(args.configs)
    object_ = configs.to_object(config)  # dict
    settings = Settings.model_validate(object_)
    with settings.job as runner:  # context
        runner.run()  # run in the context
