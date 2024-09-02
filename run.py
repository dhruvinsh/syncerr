"""Run the sync between Jellyfin and Plex."""

import logging

from loguru import logger

from syncerr.api.jellyfin import Jellyfin
from syncerr.config import cfg
from syncerr.engine import HttpEngine

try:
    LEVEL = getattr(logging, str.upper(cfg.LOG_LEVEL))
except AttributeError:
    LEVEL = logging.INFO

logger.info("Running...")

jf = Jellyfin(
    url=cfg.JELLYFIN_URL,
    username=cfg.JELLYFIN_USERNAME,
    password=cfg.JELLYFIN_PASSWORD,
    engine=HttpEngine,
)

print(jf.now_playing())
