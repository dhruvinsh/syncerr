"""Central config module."""

import logging
from dataclasses import dataclass
from pathlib import Path

from omegaconf import OmegaConf

BASE_PATH: Path = Path(".")
CONFIG_PATH = BASE_PATH / "config.yaml"


@dataclass
class ConfigTypes:
    """Config validation type check."""

    LOG_LEVEL: str
    JELLYFIN_URL: str
    JELLYFIN_USERNAME: str
    JELLYFIN_PASSWORD: str

    PLEX_URL: str
    PLEX_TOKEN: str


schema = OmegaConf.structured(ConfigTypes)
conf = OmegaConf.load(CONFIG_PATH)

cfg = OmegaConf.merge(schema, conf)

try:
    level = getattr(logging, str.upper(cfg.LOG_LEVEL))
except AttributeError:
    level = logging.INFO

LEVEL = level
