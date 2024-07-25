"""Scripts for the CLI application."""

# ruff: noqa: E402

# %% WARNINGS

import warnings

# disable annoying mlflow warnings
warnings.filterwarnings(action="ignore", category=UserWarning)

# %% IMPORTS

import argparse
import json
import sys

from bikes import settings
from bikes.io import configs

# %% PARSERS

parser = argparse.ArgumentParser(description="Run an AI/ML job from YAML/JSON configs.")
parser.add_argument("files", nargs="*", help="Config files for the job (local path only).")
parser.add_argument("-e", "--extras", nargs="*", default=[], help="Config strings for the job.")
parser.add_argument("-s", "--schema", action="store_true", help="Print settings schema and exit.")

# %% SCRIPTS


def main(argv: list[str] | None = None) -> int:
    """Main script for the application."""
    args = parser.parse_args(argv)
    if args.schema:
        schema = settings.MainSettings.model_json_schema()
        json.dump(schema, sys.stdout, indent=4)
        return 0
    files = [configs.parse_file(file) for file in args.files]
    strings = [configs.parse_string(string) for string in args.extras]
    if len(files) == 0 and len(strings) == 0:
        raise RuntimeError("No configs provided.")
    config = configs.merge_configs([*files, *strings])
    object_ = configs.to_object(config)  # python object
    setting = settings.MainSettings.model_validate(object_)
    with setting.job as runner:
        runner.run()
        return 0
