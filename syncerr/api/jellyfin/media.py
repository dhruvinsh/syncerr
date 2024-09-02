"""Module to work with Jellyfin Media object."""

import logging
from typing import TYPE_CHECKING, Any

from syncerr.schema import Movie, Series
from syncerr.schema.episode import Episode

if TYPE_CHECKING:
    from .jellyfin import Jellyfin


class JellyfinMedia:
    """Jellyfin media (Movies and Shows) processor."""

    def __init__(self, jellyfin: "Jellyfin") -> None:
        self.jf = jellyfin
        self.jf.authenticate()
        self.logger = logging.getLogger(self.__class__.__name__)

    def now_playing(self) -> list[Movie | Episode]:
        """Fetch now playing items."""
        ret = []
        items = self.jf.now_playing()
        for item in items:
            for _, item_id in item.items():
                ret.append(self.get_details(item_id))

        return ret

    def played_items(self) -> dict[Any, Any]:
        """Get already played items.

        ENDPOINT: /Users/{userId}/Items
        TYPE: GET
        PARAMS: Huge lists. look at the API
        """
        if not self.jf.is_authenticated:
            raise ValueError("Authentication is required for jellyfin")

        url = self.url + f"/Users/{self.userid}/Items"
        # currently jellyfin only supports Movies and Series only
        params = {
            "includeItemTypes": ["Movie", "Series"],
            "isPlayed": True,
        }

        resp = self.engine.get(url, params=params)

        return resp

    def movies(self) -> list[Movie]:
        """Fetch all the available movied in Jellyfin."""
        pass

    def shows(self) -> list[Series]:
        """Fetch all the available shows in Jellyfin."""
        pass


def currently_playing(jfm: JellyfinMedia) -> None:
    """
    With the help of jellyfin api find the status of currently playing video contents.
    :param jf: jellyfin object
    """
    items = jfm.now_playing()
    for item in items:
        # percentage do not appear when video is about to end or about to start in
        # that case need to pull the data from Played flag
        # if PlayedPercentage:
        #   use it
        # elif Played == True:
        #   100% done --> almost finished playing or just done
        # elif Played == False:
        #   0% done --> just started playing
        try:
            percentage = item.details.percentage
        except KeyError:
            if item.details.played:
                percentage = 100.00
            else:
                percentage = 0.00

        jfm.logger.info(
            "Currently playing: %s -> Currently Played: %0.3f%%", item.name, percentage
        )
