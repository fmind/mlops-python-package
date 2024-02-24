"""Entry point of the program."""

# %% IMPORTS

import argparse
import json

import pydantic as pdt
import pydantic_settings as pdts

from bikes import configs, jobs

# %% SETTINGS


class Settings(pdts.BaseSettings, strict=True):
    """Settings for the program.

    Attributes:
        job (jobs.JobKind): job associated with the settings.
    """

    job: jobs.JobKind = pdt.Field(..., discriminator="KIND")


# %% PARSERS

parser = argparse.ArgumentParser(description="Run a single job from external settings.")
parser.add_argument("configs", nargs="+", help="Config files for the job (local or remote).")
parser.add_argument("-e", "--extras", nargs="+", default=[], help="Config strings for the job.")
parser.add_argument("-s", "--schema", action="store_true", help="Print settings schema and exit.")

# %% SCRIPTS


def main(argv: list[str] | None = None) -> int:
    """Main function of the program.

    Args:
        argv (list[str] | None, optional): program arguments. Defaults to None for sys.argv.

    Returns:
        int: status code of the program.
    """
    args = parser.parse_args(argv)
    if args.schema is True:
        schema = Settings.model_json_schema()
        print(json.dumps(schema, indent=2))
        return 0  # success
    files = map(configs.parse_file, args.configs)
    strings = map(configs.parse_string, args.extras)
    config = configs.merge_configs([*files, *strings])
    object_ = configs.to_object(config)  # convert to dict
    settings = Settings.model_validate(object_)  # to pydantic
    with settings.job as runner:
        runner.run()  # execute job
    return 0  # success
