"""Run the sync between Jellyfin and Plex."""

from loguru import logger

from syncerr.api.jellyfin import Jellyfin
from syncerr.config import cfg
from syncerr.engine import HttpEngine

logger.info("Running...")

jf = Jellyfin(
    url=cfg.JELLYFIN_URL,
    username=cfg.JELLYFIN_USERNAME,
    password=cfg.JELLYFIN_PASSWORD,
    engine=HttpEngine,
)

print(jf.now_playing())
