"""Test the configs module."""
# pylint: disable=missing-docstring

# %% IMPORTS

import os

from omegaconf import OmegaConf

from wines import configs

# %% LOADERS


def test_load_config(tmp_path: str):
    # given
    text = """
    a: 1
    b: True
    c: [3, 4]
    """
    path = os.path.join(tmp_path, "config.yml")
    with open(path, "w", encoding="utf-8") as writer:
        writer.write(text)
    # when
    config = configs.load_config(path)
    # then
    assert config == {
        "a": 1,
        "b": True,
        "c": [3, 4],
    }, "Config should be loaded correctly!"


def test_load_configs(tmp_path: str):
    # given
    paths = []
    for i in range(3):
        text = f"""
        x: {i}
        {i}: {i}
        """
        path = os.path.join(tmp_path, f"{i}.yml")
        with open(path, "w", encoding="utf-8") as writer:
            writer.write(text)
        paths.append(path)
    # when
    config = configs.load_configs(paths)
    # then
    assert config == {
        # each file should have its key
        0: 0,
        1: 1,
        2: 2,
        # x should be the last value read
        "x": 2,
    }, "Configs should be loaded correctly!"


# %% CONVERTERS


def test_to_object():
    # given
    values = {
        "a": 1,
        "b": True,
        "c": [3, 4],
    }
    config = OmegaConf.create(values)
    # when
    object_ = configs.to_object(config)
    # then
    assert object_ == values, "Object should be the same!"
    assert isinstance(object_, dict), "Object should be a dict!"
