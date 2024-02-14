"""CLI Scripts for the program."""

# %% IMPORTS

import argparse

import pydantic as pdt
import pydantic_settings as pdts

from bikes import configs, jobs

# %% SETTINGS


class Settings(pdts.BaseSettings, strict=True):
    """Settings for the program.

    Attributes:
        job: job associated with the settings.
    """

    job: jobs.JobKind = pdt.Field(..., discriminator="KIND")


# %% PARSERS

parser = argparse.ArgumentParser(description="Run a job with configs.")
parser.add_argument("configs", nargs="+", help="Config files for the job.")

# %% SCRIPTS


def main(argv: list[str] | None = None) -> int:
    """Main function of the program.

    Args:
        argv (list[str] | None, optional): program arguments. Defaults to None for sys.argv.

    Returns:
        int: status code of the program.
    """
    args = parser.parse_args(argv)
    config = configs.parse_configs(args.configs)
    object_ = configs.to_object(config)
    settings = Settings.model_validate(object_)
    with settings.job as runner:
        runner.run()
    return 0  # success
