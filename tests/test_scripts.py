"""Test the scripts module."""
# pylint: disable=missing-docstring

# %% IMPORTS

import os
from unittest import mock

import pytest

from wines import scripts

# %% SCRIPTS


@pytest.mark.parametrize(
    "scenario",
    [
        # valid
        "tuning.yaml",
        "training.yaml",
        "inference.yaml",
        # invalid
        pytest.param("invalid.yaml", marks=pytest.mark.xfail),
    ],
)
def test_main(scenario: str, confs_path: str):
    # given
    path = os.path.join(confs_path, scenario)
    argv = [scenario, path]
    # when
    with mock.patch("sys.argv", argv):
        scripts.main()
    # then
    assert True, "Main script should not raise errors!"
