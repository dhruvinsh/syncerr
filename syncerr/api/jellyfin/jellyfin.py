"""
Author: Dhruvin Shah
Very minimal endpoints added here that just get work done
"""

import logging
from typing import TYPE_CHECKING, Any, Union

from pydantic import Json

from syncerr.util import filter_dict

from .schema import Detail, Episode, Movie, Season, Series

if TYPE_CHECKING:
    from syncerr.engine import HttpEngine


class Jellyfin:
    """
    Minimal Jellyfin api

    Currently authentication done via username and password for jellyfin.

    :param url: jellyfin server url
    :param username: jellyfin username
    :param password: jellyfin password
    """

    CLIENT: str = "syncerr"
    DEVICE: str = "syncerr-api"
    DEVICE_ID: str = "4226af2e-a4fa-43e5-8d4c-f6a9f6de181e"
    VERSION: str = "1.0.0"

    def __init__(
        self, url: str, username: str, password: str, engine: type["HttpEngine"]
    ) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.url = url.rstrip("/")
        self.username = username
        self.password = password

        # NOTE: all values in the header are case-sensitive
        # TODO: figureout UUID4 way
        emby_auth = (
            "MediaBrowser , "
            f'Client="{self.CLIENT}", '
            f'Device="{self.DEVICE}", '
            f'DeviceId="{self.DEVICE_ID}", '
            f'Version="{self.VERSION}"'
        )
        headers: dict[str, str] = {"X-Emby-Authorization": emby_auth}

        self.engine = engine(headers=headers)

        # authenticate to obtained the AccessToken for given user
        auth = self.authenticate()
        # populate the userid which can be used afterwards
        self.userid = auth["User"]["Id"]
        token = auth["AccessToken"]

        # with authentication, lets update the existing header
        new_value = f'{emby_auth}, Token="{token}"'
        headers["X-Emby-Authorization"] = new_value

        # updating header for httpx session
        self.engine.session.headers.update(headers)

    def authenticate(self) -> Json:
        """
        Authentication for jellyfin. It is performed via username and password.

        API can only be created via the admin user if done so non-admin user can not
        take advantage of this API.

        endpoint: /Users/AuthenticateByName
        type: POST
        payload: { "Username": str, "Pw": str }
        """
        url = self.url + "/Users/AuthenticateByName"
        data = {"Username": self.username, "Pw": self.password}

        res = self.engine.post(url, json=data)
        self.logger.debug("authentication: %s", res)

        return res.json()

    def now_playing(self) -> list[str]:
        """
        Get currently playing media.

        ENDPOINT: /Sessions
        TYPE: GET
        PARAMS: {"activeWithinSeconds": int }

        :return: list of id only

        NOTE: params are options but setting them helps for faster requests.
        """
        url = self.url + "/Sessions"
        # get active session in last 16 min
        params = {"activeWithinSeconds": 960}

        # call to endpoint get list of SessionInfo schema
        # get list of data with NowPlayingItem: {...} only
        sessions = self.engine.get(url, filter_keys=["NowPlayingItem"], params=params)
        self.logger.debug(sessions)

        items = []
        for session in sessions:
            if not session:
                continue

            now_playing = filter_dict(session["NowPlayingItem"], keys=["Id"])
            if not now_playing:
                # looks like filter is broken its not wokring
                raise ValueError("Not able find any data from NowPlayingItem")

            self.logger.debug(now_playing)
            items.append(now_playing)

        self.logger.info("found total %s items being played.", len(items))
        return items

    def _get_details(self, item_id: str) -> Json:
        """
        For given item id get the details
        :param cid: content id to get details for

        ENDPOINT: /Users/{userId}/Items/{itemId}
        TYPE: GET
        PARAMS: BaseItemDto {...}
        """
        url = self.url + f"/Users/{self.userid}/Items/{item_id}"

        # filter keys that I need from BaseItemDto
        keys = [
            "Id",
            "IndexNumber",  # potential episode number
            "Name",
            "ParentIndexNumber",  # potential season number
            "Path",
            "RunTimeTicks",
            "SeasonId",
            "SeasonName",
            "SeriesId",
            "SeriesName",
            "SortName",
            # to see if its movie or series, value could be Episode or Movie
            "Type",
            "UserData",
        ]
        return self.engine.get(url, filter_keys=keys)

    def get_details(self, item_id: str) -> Union[Movie, Series]:
        """
        For given item id get the details
        :param cid: content id to get details for

        ENDPOINT: /Users/{userId}/Items/{itemId}
        TYPE: GET
        PARAMS: BaseItemDto {...}
        """
        item_detail = self._get_details(item_id)
        self.logger.debug(item_detail)

        match item_detail["Type"]:
            case "Episode":
                return self.season_builder(
                    item_detail["SeriesId"], item_detail["SeasonId"], item_id
                )
            case "Movie":
                return self.movie_builder(item_id["Id"])
            case _:
                raise ValueError("Unsupported media type found")

    def season_builder(self, series_id: str, season_id: str, episode_id: str) -> Series:
        """
        :param series_id: series id number
        :param season_id: season id number
        :param episode_id: episond id number
        """
        series_detail = self._get_details(series_id)
        season_detail = self._get_details(season_id)
        episode_detail = self._get_details(episode_id)
        detail = self._get_details(episode_id)["UserData"]

        details = Detail(
            percentage=detail["PlayedPercentage"],
            playback_time=detail["PlaybackPositionTicks"],
            play_count=detail["PlayCount"],
            last_played=detail["LastPlayedDate"],
            played=detail["Played"],
            key=detail["Key"],
        )

        episode = Episode(
            name=episode_detail["Name"],
            id=episode_detail["Id"],
            run_time=episode_detail["RunTimeTicks"],
            index=episode_detail["IndexNumber"],
            details=details,
        )

        season = Season(
            name=season_detail["Name"],
            id=season_detail["Id"],
            index=season_detail["IndexNumber"],
            episodes=[episode],
        )

        series = Series(
            name=series_detail["Name"], id=series_detail["Id"], seasons=[season]
        )

        return series

        try:
            percentage = item_detail["UserData"]["PlayedPercentage"]
        except KeyError:
            if item_detail["UserData"]["Played"]:
                percentage = 100.00
            else:
                percentage = 0.00
        if item_detail["Type"] == "Episode":
            self.logger.info(
                "Currently playing: %s - %s - %s -> Currently Played: %0.3f%%",
                item_detail["SeriesName"],
                item_detail["SeasonName"],
                item_detail["Name"],
                percentage,
            )
        elif item_detail["Type"] == "Movie":
            self.logger.info(
                "Currently playing: %s --> Currently Played: %0.3f%%",
                item_detail["Name"],
                percentage,
            )
        else:
            self.logger.error(
                "For %s unknow type found: %s", item_detail["Name"], item_detail["Type"]
            )
        return item_detail

    def movie_builder(self, item_id: str) -> Movie:
        """ """
        movie_detail = self._get_details(item_id)
        detail = movie_detail["UserData"]

        details = Detail(
            percentage=detail["PlayedPercentage"],
            playback_time=detail["PlaybackPositionTicks"],
            play_count=detail["PlayCount"],
            last_played=detail["LastPlayedDate"],
            played=detail["Played"],
            key=detail["Key"],
        )
        return Movie(
            name=movie_detail["Name"],
            id=movie_detail["Id"],
            run_time=movie_detail["RunTimeTicks"],
            details=details,
        )

    def played_items(self) -> dict[Any, Any]:
        """
        Get already played items.

        ENDPOINT: /Users/{userId}/Items
        TYPE: GET
        PARAMS: Huge lists. look at the API
        """
        url = self.url + f"/Users/{self.userid}/Items"
        # currently jellyfin only supports Movies and Series only
        params = {
            "includeItemTypes": ["Movie", "Series"],
            "isPlayed": True,
        }

        resp = self.engine.get(url, params=params)

        self.logger.debug(resp)

        return resp

    def movies(self, movie_id: str) -> list[Movie]:
        """
        get all the jellyfin movie with details

        ENDPOINT: /Users/{userId}/Items
        TYPE: GET
        PARAMS: ParentId
        """
        ret = []

        url = self.url + f"/Users/{self.userid}/Items"
        params = {"ParentId": movie_id}

        resp = self.engine.get(url, params=params)

        if not isinstance(resp, dict):
            raise ValueError("proper data not found")

        for movie in resp["Items"]:
            name = movie["Name"]
            id = movie["Id"]
            run_time = int(movie["RunTimeTicks"])
            ret.append(Movie(name=name, id=id, run_time=run_time, details=None))

        return ret


def currently_playing(jf: Jellyfin) -> list[dict[str, Any]]:
    """
    With the help of jellyfin api find the status of currently playing video contents.
    :param jf: jellyfin object
    """
    jf.authenticate()
    items = jf.now_playing()
    details: list[dict[str, Any]] = []
    for item in items:
        detail = jf.get_details(item)

        # percentage do not appear when video is about to end or about to start in
        # that case need to pull the data from Played flag
        # if PlayedPercentage:
        #   use it
        # elif Played == True:
        #   100% done --> almost finished playing or just done
        # elif Played == False:
        #   0% done --> just started playing
        try:
            percentage = detail["UserData"]["PlayedPercentage"]
        except KeyError:
            if detail["UserData"]["Played"]:
                percentage = 100.00
            else:
                percentage = 0.00

        # Currently API works with Episode or Movie only
        if detail["Type"] == "Episode":
            jf.logger.info(
                "Currently playing: %s - %s - %s -> Currently Played: %0.3f%%",
                detail["SeriesName"],
                detail["SeasonName"],
                detail["Name"],
                percentage,
            )
        elif detail["Type"] == "Movie":
            jf.logger.info(
                "Currently playing: %s --> Currently Played: %0.3f%%",
                detail["Name"],
                percentage,
            )
        else:
            jf.logger.error(
                "For %s unknow type found: %s", detail["Name"], detail["Type"]
            )

        detail["percentage"] = percentage
        details.append(detail)
    return details
