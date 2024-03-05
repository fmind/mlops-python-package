# %% IMPORTS

import json
import os
import typing as T

import pytest
from bikes import scripts

# %% SCRIPTS


def test_schema(capsys: T.Any) -> None:
    # given
    argv = ["prog", "--schema"]
    # when
    scripts.main(argv)
    captured = capsys.readouterr()
    # then
    assert captured.err == "", "Capture error should be empty!"
    assert json.loads(captured.out), "Capture output should be a valid JSON!"


@pytest.mark.parametrize(
    "scenario",
    [
        # passed
        "valid",
        # failure
        pytest.param("invalid", marks=pytest.mark.xfail),
    ],
)
def test_main(scenario: str, confs_path: str, extra_config: str) -> None:
    # given
    root = os.path.join(confs_path, scenario)
    # when
    for path in sorted(os.listdir(root)):
        config = os.path.join(root, path)
        argv = [config, "-e", extra_config]
        print("Running main with:", argv)
        status = scripts.main(argv=argv)
        # then
        assert status == 0, "Main should return 0!"
