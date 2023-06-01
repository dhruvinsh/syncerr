"""
Main module
"""
import logging
import time

from syncerr import Jellyfin, Plex, currently_playing
from syncerr.config import cfg
from syncerr.engine import HttpEngine
from syncerr.logger import setup_logger

try:
    LEVEL = getattr(logging, str.upper(cfg.LOG_LEVEL))
except AttributeError:
    LEVEL = logging.INFO

setup_logger(LEVEL)
logger = logging.getLogger("syncerr")

jellyfin = Jellyfin(
    cfg.JELLYFIN_URL,
    username=cfg.JELLYFIN_USERNAME,
    password=cfg.JELLYFIN_PASSWORD,
    engine=HttpEngine,
)
breakpoint()
# Fetch currently playing media on Jellyfin
jf_media = currently_playing(jellyfin)


plex = Plex(cfg.PLEX_URL, cfg.PLEX_TOKEN)
libraries = plex.library_types()

plex_media = {}
for library in libraries:
    # Interested in the shows and movies only
    if library["type"] in ["movie", "show"]:
        lib_key = library["key"]

        plex_media[library["type"]] = plex.items(lib_key)

for show in plex_media["show"]:
    logger.info("working on %s", show["title"])
    show["details"] = plex.traverse_child(show["ratingKey"])
    # FIX: this sleep is here to throttle the requests.
    time.sleep(0.2)

for jm in jf_media:
    IS_MOVIE = True
    if jm["Type"] == "Episode":
        IS_MOVIE = False
        plex_items = plex_media["show"]
    else:
        plex_items = plex_media["movie"]

    for pm in plex_items:
        jf_media_name = jm["Name"] if IS_MOVIE else jm["SeriesName"]
        if jf_media_name.lower() == pm["title"].lower():
            # we found the match in plex
            if IS_MOVIE:
                # since media type is movie on jellyfin it is easy to push progress on
                # plex
                plex.mark_status(pm, progress=jm["percentage"])
                logger.info("Movie update pushed to Plex")
            else:
                # we need to find the plex object
                for season in pm["details"]:
                    if jm["SeasonName"].lower() == season["title"].lower():
                        # we found the correct season
                        for episode in season["episodes"]:
                            if jm["Name"].lower() == episode["title"].lower():
                                plex.mark_status(episode, progress=jm["percentage"])
                                logger.info("Episode update pushed to Plex")
                                break
                        break

            break
logger.info("Done pushing data from Jellyfin to Plex")
