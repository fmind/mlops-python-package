# %% IMPORTS

import json
import os

import pydantic as pdt
import pytest
from _pytest import capture as pc
from regression_model_template import scripts

# %% SCRIPTS


def test_schema(capsys: pc.CaptureFixture[str]) -> None:
    # given
    args = ["prog", "--schema"]
    # when
    scripts.main(args)
    captured = capsys.readouterr()
    # then
    assert captured.err == "", "Captured error should be empty!"
    assert json.loads(captured.out), "Captured output should be a JSON!"


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
        assert status == 0, f"Job should succeed for config: {config}"


def test_main__no_configs() -> None:
    # given
    argv: list[str] = []
    # when
    with pytest.raises(RuntimeError) as error:
        scripts.main(argv)
    # then
    assert error.match("No configs provided."), "RuntimeError should be raised!"
