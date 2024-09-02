"""Minimal Jellyfin api for syncerr."""

import sys
from typing import TYPE_CHECKING, Any

from loguru import logger
from pydantic import Json

from syncerr.encap import NowPlayingData
from syncerr.schema import Detail, Episode, Movie
from syncerr.util import filter_dict

if TYPE_CHECKING:
    from syncerr.engine import HttpEngine


class Jellyfin:
    """Jellyfin API.

    Currently authentication done via username and password for jellyfin.
    """

    CLIENT: str = "syncerr"
    DEVICE: str = "syncerr-api"
    # TODO: find a way to generate unique device id or pass as env
    DEVICE_ID: str = "4226af2e-a4fa-43e5-8d4c-f6a9f6de181e"
    VERSION: str = "1.0.0"

    def __init__(
        self, url: str, username: str, password: str, engine: type["HttpEngine"]
    ) -> None:
        """Constructor.

        :param url: jellyfin server url
        :param username: jellyfin username
        :param password: jellyfin password
        :param engine: http engine with which requests can be made.
        """
        self.url = url.rstrip("/")
        self.username = username
        self.password = password
        self.is_authenticated = False
        self.engine = self.build_engine(engine)

    def build_engine(self, engine: type["HttpEngine"]) -> "HttpEngine":
        """Build http engine with proper headers.

        :param engine: http engine.
        """
        # NOTE: all values in the header are case-sensitive
        emby_auth = (
            "MediaBrowser , "
            f'Client="{self.CLIENT}", '
            f'Device="{self.DEVICE}", '
            f'DeviceId="{self.DEVICE_ID}", '
            f'Version="{self.VERSION}"'
        )
        headers = {"X-Emby-Authorization": emby_auth}

        session = engine(headers=headers)

        # authenticate to obtained the AccessToken for given user
        auth = self.authenticate(session)

        if auth is None:
            # validation failed
            logger.error("Please check the username password for jellyfin")
            sys.exit(1)

        # populate the userid which can be used afterwards
        self.userid = auth["User"]["Id"]
        token = auth["AccessToken"]

        # with authentication, lets update the existing header
        new_value = f'{emby_auth}, Token="{token}"'
        headers["X-Emby-Authorization"] = new_value

        # updating header for httpx session
        session.session.headers.update(headers)

        return session

    @property
    def is_authenticated(self) -> bool:
        """Status flag to track jellyfin authentication."""
        return self._is_authenticated

    @is_authenticated.setter
    def is_authenticated(self, value: bool) -> None:
        assert value in [True, False]
        self._is_authenticated = value

    def authenticate(self, session: "HttpEngine") -> Json[Any] | None:
        """Authentication for jellyfin. It is performed via username and password.

        API can only be created via the admin user if done so non-admin user can not
        take advantage of this API.

        endpoint: /Users/authenticatebyname
        type: POST
        payload: { "Username": str, "Pw": str }
        """
        url = self.url + "/Users/authenticatebyname"
        data = {"Username": self.username, "Pw": self.password}

        res = session.post(url, json=data)

        # validate the response code
        if res.status_code != 200:
            logger.error("Could not able to validate the jellyfin")
            return None

        self.is_authenticated = True

        return res.json()

    def get_details(self, item_id: str) -> Json[Any]:
        """For given item id get the details.

        :param cid: content id to get details for

        ENDPOINT: /Users/{userId}/Items/{itemId}
        TYPE: GET
        PARAMS: BaseItemDto {...}
        """
        if not self.is_authenticated:
            raise ValueError("Authentication is required for jellyfin")

        url = self.url + f"/Users/{self.userid}/Items/{item_id}"

        # selective fields from BaseItemDto
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
            "UserData",  # UserData holds all the details data
        ]
        return self.engine.get(url, filter_keys=keys)

    def now_playing_json(self, active_time: int = 900) -> Json[Any]:
        """Get currently playing media.

        ENDPOINT: /Sessions
        TYPE: GET
        PARAMS: {"activeWithinSeconds": int }

        :return: list of id only

        NOTE: params are options but setting them helps for faster requests.
        """
        if not self.is_authenticated:
            raise ValueError("Authentication is required for jellyfin")

        url = self.url + "/Sessions"
        # get active session in last 15 min
        params = {"activeWithinSeconds": active_time}

        # call to endpoint get list of SessionInfo schema
        # get list of data with NowPlayingItem: {...} only
        sessions = self.engine.get(url, filter_keys=["NowPlayingItem"], params=params)
        logger.debug(sessions)

        items = []
        for session in sessions:
            if not session:
                continue

            now_playing = filter_dict(session["NowPlayingItem"], keys=["Id", "Type"])
            if not now_playing:
                # looks like filter is broken its not wokring
                raise ValueError("Not able find any data from NowPlayingItem")

            items.append(
                NowPlayingData(cid=now_playing["Id"], ctype=now_playing["Type"])
            )

        logger.info("found total %s items being played.", len(items))
        return items

    def now_playing(self, active_time: int = 900) -> list[Movie | Episode]:
        """Fetch recently played content for the given time.

        :param active_time: time in seconds to check for active session.
            default is 15 min.
        """
        res: list[Movie | Episode] = []
        items = self.now_playing_json(active_time)

        for item in items:
            item_detail = self.get_details(item.cid)
            match item.ctype.lower():
                case "episode":
                    res.append(self.episode(item_detail=item_detail))
                case "movie":
                    res.append(self.movie(item_detail=item_detail))
                case _:
                    raise ValueError("Unsupported media type found")

        return res

    def movie(self, item_detail: NowPlayingData) -> Movie:
        """Get movie details.

        ENDPOINT: /Users/{userId}/Items
        TYPE: GET
        PARAMS: ParentId
        """
        detail = item_detail["UserData"]

        details = Detail(
            percentage=detail["PlayedPercentage"],
            playback_time=detail["PlaybackPositionTicks"],
            play_count=detail["PlayCount"],
            last_played=detail["LastPlayedDate"],
            played=detail["Played"],
            key=detail["Key"],
        )

        return Movie(
            name=item_detail["Name"],
            item_id=item_detail["Id"],
            run_time=item_detail["RunTimeTicks"],
            details=details,
        )

    def episode(self, item_detail: Json[Any]) -> Episode:
        """Get episode details.

        ENDPOINT: /Users/{userId}/Items
        TYPE: GET
        PARAMS: ParentId
        """
        params = {"ParentId": item_detail["Id"]}
        data = self.engine.get(self.url + f"/Users/{self.userid}/Items", params=params)
        detail = item_detail["UserData"]

        details = Detail(
            percentage=detail["PlayedPercentage"],
            playback_time=detail["PlaybackPositionTicks"],
            play_count=detail["PlayCount"],
            last_played=detail["LastPlayedDate"],
            played=detail["Played"],
            key=detail["Key"],
        )

        return Episode(
            name=item_detail["Name"],
            id=item_detail["Id"],
            run_time=item_detail["RunTimeTicks"],
            index=item_detail["IndexNumber"],
            details=details,
        )
