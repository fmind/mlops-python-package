"""Scripts for the CLI application."""

# %% IMPORTS

import argparse
import json
import sys

from bikes import settings
from bikes.io import configs

# %% PARSERS

parser = argparse.ArgumentParser(description="Run an AI/ML job fron YAML/JSON configs.")
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
    files = map(configs.parse_file, args.files)
    strings = map(configs.parse_string, args.extras)
    config = configs.merge_configs([*files, *strings])
    object_ = configs.to_object(config)  # python object
    setting = settings.MainSettings.model_validate(object_)
    with setting.job as runner:
        runner.run()
        return 0
