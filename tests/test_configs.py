# %% IMPORTS

import os

from bikes import configs
from omegaconf import OmegaConf

# %% LOADERS


def test_parse_file(tmp_path: str):
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
    config = configs.parse_file(path)
    # then
    assert config == {
        "a": 1,
        "b": True,
        "c": [3, 4],
    }, "File config should be loaded correctly!"


def test_parse_string():
    # given
    text = """{"a": 1, "b": 2, "data": [3, 4]}"""
    # when
    config = configs.parse_string(text)
    # then
    assert config == {
        "a": 1,
        "b": 2,
        "data": [3, 4],
    }, "String config should be loaded correctly!"


def test_merge_configs():
    # given
    confs = [OmegaConf.create({"x": i, i: i}) for i in range(3)]
    # when
    config = configs.merge_configs(confs)
    # then
    assert config == {
        0: 0,
        1: 1,
        2: 2,
        "x": 2,
    }, "Configs should be merged correctly!"


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
