"""
Author: Dhruvin Shah
Very minimal endpoints added here that just get work done
"""

from typing import Any, Optional

import httpx

from syncerr.logger import create_logger
from syncerr.util import filter_dict


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

    def __init__(self, url: str, username: str, password: str) -> None:
        self.logger = create_logger(self.__class__.__name__)

        self.url: str = url
        self.username = username
        self.password = password

        # httpx client that by default follow redirections
        # NOTE: all values in the header are case-sensitive
        # TODO: figureout UUID4 way
        headers: dict[str, str] = {
            # pylint: disable=line-too-long
            "X-Emby-Authorization": f'MediaBrowser Client="{self.CLIENT}", Device="{self.DEVICE}", DeviceId="{self.DEVICE_ID}", Version="{self.VERSION}"'
        }
        self.sess = httpx.Client(follow_redirects=True, headers=headers)

        # authenitcate to obtained the AccessToken for given user
        auth = self.authenitcate()
        # populate the userid which can be used afterwards
        self.userid = auth["User"]["Id"]
        token = auth["AccessToken"]

        # with authentication, lets update the existing header
        new_value = f'{headers["X-Emby-Authorization"]}, Token="{token}"'
        headers["X-Emby-Authorization"] = new_value

        # updating header for httpx session
        self.sess.headers.update(headers)  # type: ignore

    def _call(
        self,
        method: str,
        url: str,
        *,
        filter_keys: Optional[list[str]] = None,
        **kwargs,
    ) -> Any:
        """
        General method to call url. It returns the json object and applies filter_keys
        to it befor that.

        :param method: method to use to call the url, valid values are get, post
        :param url: endpoint that need to call
        :param filter_keys: for jsonified object applie filter to obtain certain keys
                            only
        :param kwargs: all the options that applies to rest call
        """
        assert method in ["get", "post"]

        fetch = getattr(self.sess, method)
        resp = fetch(url, **kwargs)
        res = resp.json()

        keys = [] if filter_keys is None else filter_keys

        if not keys:
            return res

        # if response is list of dicts then filter need to apply to each dict
        if isinstance(res, list):
            return list(map(lambda r: filter_dict(r, keys=keys), res))

        return filter_dict(res, keys)

    def authenitcate(self) -> dict[str, Any]:
        """
        Authentication for jellyfin

        endpoint: /Users/AuthenticateByName
        type: POST
        payload: { "Username": str, "Pw": str }
        """
        url = self.url + "/Users/AuthenticateByName"
        data = {"Username": self.username, "Pw": self.password}

        res = self._call("post", url, json=data)
        self.logger.debug("authentication: %s", res)

        return res

    def currently_playing(self) -> list[dict[str, Any]]:
        """
        Get currently playing media.

        ENDPOINT: /Sessions
        TYPE: GET
        PARAMS: {"activeWithinSeconds": int }

        NOTE: params are options but setting them helps for fater requests.
        """
        url = self.url + "/Sessions"
        # get active session in last 16 min
        params = {"activeWithinSeconds": 960}

        # call to endpoint get list of SessionInfo schema
        # get list of data with NowPlayingItem: {...} only
        play_sessions = self._call(
            "get", url, filter_keys=["NowPlayingItem"], params=params
        )
        self.logger.debug(play_sessions)

        items = []
        for session in play_sessions:
            if not session:
                continue

            # out of NowPlayingItem session get specific data only
            filter_keys: list[str] = [
                "Name",
                "Id",
                "Path",
                "ParentId",
                "Type",
                "SeriesName",
                "SeriesId",
                "SeasonId",
                "SeasonName",
            ]

            now_playing = filter_dict(session["NowPlayingItem"], keys=filter_keys)
            if not now_playing:
                # looks like filter is broken its not wokring
                self.logger.error("Not able find any data from NowPlayingItem")
                continue

            self.logger.debug(now_playing)
            items.append(now_playing)

        self.logger.info("found total %s items being played.", len(items))
        return items

    def get_details(self, item: str) -> dict[str, Any]:
        """
        For given item id get the details
        :param item: id to get details

        ENDPOINT: /Users/{userId}/Items/{itemId}
        TYPE: GET
        PARAMS: BaseItemDto {...}
        """
        url = self.url + f"/Users/{self.userid}/Items/{item}"

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
        item_detail = self._call("get", url, filter_keys=keys)
        self.logger.debug(item_detail)

        return item_detail



def currently_playing(jf: Jellyfin):
    """
    With the help of jellyfin api find the status of currently playing video contents.
    :param jf: jellyfin object
    """
    jf.authenitcate()
    items = jf.currently_playing()
    for item in items:
        details = jf.get_details(item.get("Id"))  # type: ignore

        # percentage do not appear when video is about to end or about to start in
        # that case need to pull the data from Played flag
        # if PlayedPercentage:
        #   use it
        # elif Played == True:
        #   100% done --> almost finished playing or just done
        # elif Played == False:
        #   0% done --> just started playing
        try:
            percentage = details["UserData"]["PlayedPercentage"]
        except KeyError:
            if details["UserData"]["Played"]:
                percentage = 100.00
            else:
                percentage = 0.00

        # Currently API works with Episode or Movie only
        if details["Type"] == "Episode":
            jf.logger.info(
                "Currently playing: %s - %s - %s -> Currently Played: %0.3f%%",
                details["SeriesName"],
                details["SeasonName"],
                details["Name"],
                percentage,
            )
        elif details["Type"] == "Movie":
            jf.logger.info(
                "Currently playing: %s --> Currently Played: %0.3f%%",
                details["Name"],
                percentage,
            )
        else:
            jf.logger.error(
                "For %s unknow type found: %s", details["Name"], details["Type"]
            )
