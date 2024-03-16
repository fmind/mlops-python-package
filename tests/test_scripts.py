# %% IMPORTS

import json
import os

import pydantic as pdt
import pytest
from _pytest import capture as pc
from bikes import scripts

# %% SCRIPTS


def test_schema(capsys: pc.CaptureFixture[str]) -> None:
    # given
    args = ["prog", "--schema"]
    # when
    scripts.main(args)
    capture = capsys.readouterr()
    # then
    assert capture.err == "", "Captured error should be empty!"
    assert json.loads(capture.out), "Captured output should be a JSON!"


@pytest.mark.parametrize(
    "scenario",
    [
        "valid",
        pytest.param(
            "invalid",
            marks=pytest.mark.xfail(
                reason="Invalid config.",
                raises=pdt.ValidationError,
            ),
        ),
    ],
)
def test_main(scenario: str, confs_path: str, extra_config: str) -> None:
    # given
    folder = os.path.join(confs_path, scenario)
    confs = list(sorted(os.listdir(folder)))
    # when
    for conf in confs:  # one job per config
        config = os.path.join(folder, conf)
        argv = [config, "-e", extra_config]
        status = scripts.main(argv=argv)
        # then
        assert status == 0, f"Job should succeed with status 0! Config: {config}"
