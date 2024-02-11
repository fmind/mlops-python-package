"""Parse and merge config files."""

# %% IMPORTS

from cloudpathlib import AnyPath
from omegaconf import DictConfig, ListConfig, OmegaConf

# %% TYPES

Config = ListConfig | DictConfig

# %% LOADERS


def parse_config(path: str) -> Config:
    """Load a config file."""
    any_path = AnyPath(path)
    # pylint: disable=no-member
    text = any_path.read_text()  # type: ignore
    config = OmegaConf.create(text)
    return config


def parse_configs(paths: list[str]) -> Config:
    """Load and merge config files."""
    configs = map(parse_config, paths)
    config = OmegaConf.merge(*configs)
    return config


# %% CONVERTERS


def to_object(config: Config) -> object:
    """Convert a config to a python object."""
    return OmegaConf.to_container(config, resolve=True)
