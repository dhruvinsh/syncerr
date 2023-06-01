"""
Central config module
"""

import logging
from pathlib import Path

from omegaconf import OmegaConf

BASE_PATH: Path = Path(".")
CONFIG_PATH = BASE_PATH / "config.yaml"

cfg = OmegaConf.load(CONFIG_PATH)

try:
    LEVEL = getattr(logging, str.upper(cfg.LOG_LEVEL))
except AttributeError:
    LEVEL = logging.INFO
