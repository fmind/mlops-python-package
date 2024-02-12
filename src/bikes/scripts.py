"""CLI Scripts for the program."""

# %% IMPORTS

import argparse

import pydantic as pdt
import pydantic_settings as pdts

from bikes import configs, jobs

# %% SETTINGS


class Settings(pdts.BaseSettings, strict=True):
    """Settings for the program."""

    job: jobs.JobKind = pdt.Field(..., discriminator="KIND")


# %% PARSERS

parser = argparse.ArgumentParser(description="Run a job with configs.")
parser.add_argument("configs", nargs="+", help="Config files for a single job.")

# %% SCRIPTS


def main(argv: list[str] | None = None) -> int:
    """Main function of the script."""
    args = parser.parse_args(argv)  # argv or sys.argv
    config = configs.parse_configs(args.configs)
    object_ = configs.to_object(config)  # dict
    settings = Settings.model_validate(object_)
    with settings.job as runner:  # context
        runner.run()  # run in the context
    return 0  # 0 = success
