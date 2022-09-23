"""
Central config module
"""

from pathlib import Path

from omegaconf import OmegaConf

BASE_PATH: Path = Path(".")
CONFIG_PATH = BASE_PATH / "config.yaml"

cfg = OmegaConf.load(CONFIG_PATH)
