"""Parse and merge config files."""

# %% IMPORTS

from cloudpathlib import AnyPath
from omegaconf import DictConfig, ListConfig, OmegaConf

# %% TYPES

# Union of OmegaConf config types
Config = ListConfig | DictConfig

# %% LOADERS


def parse_config(path: str) -> Config:
    """Parse a config file from a path.

    Args:
        path (str): local or remote path.

    Returns:
        Config: representation of the config file.
    """
    any_path = AnyPath(path)
    # pylint: disable=no-member
    text = any_path.read_text()  # type: ignore
    config = OmegaConf.create(text)
    return config


def parse_configs(paths: list[str]) -> Config:
    """Parse and merge config files from paths.

    Args:
        paths (list[str]): list of local or remote paths.

    Returns:
        Config: representation of the config file.
    """
    configs = map(parse_config, paths)
    config = OmegaConf.merge(*configs)
    return config


# %% CONVERTERS


def to_object(config: Config) -> object:
    """Convert a config to a python object.

    Args:
        config (Config): representation of the config file.

    Returns:
        object: conversion of the config to a python object.
    """
    return OmegaConf.to_container(config, resolve=True)
