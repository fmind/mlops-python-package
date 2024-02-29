"""Parse, merge, and convert YAML configs."""

# %% IMPORTS

import typing as T

from omegaconf import DictConfig, ListConfig, OmegaConf

# %% TYPES

Config = ListConfig | DictConfig

# %% PARSERS


def parse_file(path: str) -> Config:
    """Parse a config file from a path.

    Args:
        path (str): local or remote path.

    Returns:
        Config: representation of the config file.
    """
    return OmegaConf.load(path)


def parse_string(string: str) -> Config:
    """Parse the given config string.

    Args:
        string (str): configuration string.

    Returns:
        Config: representation of the config string.
    """
    return OmegaConf.create(string)


# %% MERGERS


def merge_configs(configs: T.Sequence[Config]) -> Config:
    """Merge a list of config objects into one.

    Args:
        configs (list[Config]): list of config objects.

    Returns:
        Config: representation of the merged config objects.
    """
    return OmegaConf.merge(*configs)


# %% CONVERTERS


def to_object(config: Config) -> object:
    """Convert a config object to a python object.

    Args:
        config (Config): representation of the config.

    Returns:
        object: conversion of the config to a python object.
    """
    return OmegaConf.to_container(config, resolve=True)
