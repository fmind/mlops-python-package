"""Test the scripts module."""

# pylint: disable=missing-docstring

# %% IMPORTS

import os

import pytest

from bikes import scripts

# %% SCRIPTS


@pytest.mark.parametrize(
    "scenario",
    [
        # passed
        "valid",
        # failure
        pytest.param("invalid", marks=pytest.mark.xfail),
    ],
)
def test_main(scenario: str, confs_path: str):
    # given
    root = os.path.join(confs_path, scenario)
    # when
    for path in sorted(os.listdir(root)):
        conf = os.path.join(root, path)
        status = scripts.main(argv=[conf])
        # then
        assert status == 0, "Main should return 0!"
