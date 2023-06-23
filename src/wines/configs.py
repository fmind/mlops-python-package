"""Read, convert, and manage config files."""

# %% IMPORTS

import typing as T

from cloudpathlib import AnyPath
from omegaconf import DictConfig, ListConfig, OmegaConf

# %% TYPINGS

Config = T.Union[ListConfig, DictConfig]

# %% LOADERS


def load_config(path: str) -> Config:
    """Load a configuration file."""
    any_path = AnyPath(path)
    # pylint: disable=no-member
    text = any_path.read_text()  # type: ignore
    config = OmegaConf.create(text)
    return config


def load_configs(paths: T.List[str]) -> Config:
    """Load configuration files."""
    configs = map(load_config, paths)
    config = OmegaConf.merge(*configs)
    return config


# %% CONVERTERS


def to_object(config: Config) -> object:
    """Convert a config to a python object."""
    return OmegaConf.to_container(config, resolve=True)
