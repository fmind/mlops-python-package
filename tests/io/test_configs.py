# %% IMPORTS

import os

import omegaconf as oc
import pytest
import pytest_mock

from bikes.io import configs

# %% PARSERS


def test_parse_file(tmp_path: str) -> None:
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
    }, "File config should be parsed correctly!"


def test_parse_string() -> None:
    # given
    text = """{"a": 1, "b": 2, "data": [3, 4]}"""
    # when
    config = configs.parse_string(text)
    # then
    assert config == {
        "a": 1,
        "b": 2,
        "data": [3, 4],
    }, "String config should be parsed correctly!"


# %% MERGERS


def test_merge_configs() -> None:
    # given
    confs = [oc.OmegaConf.create({"x": i, i: i}) for i in range(3)]
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


def test_to_object() -> None:
    # given
    values = {
        "a": 1,
        "b": True,
        "c": [3, 4],
    }
    config = oc.OmegaConf.create(values)
    # when
    object_ = configs.to_object(config)
    # then
    assert object_ == values, "Object should be the same!"
    assert isinstance(object_, dict), "Object should be a dict!"


def test_merge_rejects_unsupported_config(mocker: pytest_mock.MockerFixture) -> None:
    mocker.patch.object(oc.OmegaConf, "merge", return_value=oc.OmegaConf.create((1, 2)))
    with pytest.raises(TypeError, match="Only mapping or list"):
        configs.merge_configs([])


def test_to_object_rejects_missing_required_values() -> None:
    config = oc.OmegaConf.create({"required": oc.MISSING})
    with pytest.raises(oc.errors.MissingMandatoryValue):
        configs.to_object(config)
