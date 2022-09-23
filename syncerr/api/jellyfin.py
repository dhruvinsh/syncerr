"""
Author: Dhruvin Shah
Very minimal endpoints added here that just get work done
"""

from typing import Any

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
        self.logger = create_logger("jellyfin")

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

    def authenitcate(self) -> dict[str, Any]:
        """
        Authentication for jellyfin

        endpoint: /Users/AuthenticateByName
        type: POST
        payload: { "Username": str, "Pw": str }
        """
        url = self.url + "/Users/AuthenticateByName"
        payload = {"Username": self.username, "Pw": self.password}

        resp = self.sess.post(url, json=payload)

        res = resp.json()
        self.logger.debug("authentication: %s", res)

        return res

    def current_playing(self) -> list[dict[str, Any]]:
        """
        Get currently playing media.

        endpoint: /Sessions
        type: GET
        params: { "controllableByUserId": str, "activeWithinSeconds": int }

        NOTE: params are options but setting them helps for fater requests.
        """
        url = self.url + "/Sessions"
        # get active session in last 16 min
        params = {"controllableByUserId": self.userid, "activeWithinSeconds": 960}

        resp = self.sess.get(url, params=params)

        # list of SessionInfo schema
        sessions = resp.json()
        self.logger.debug("current_playing: %s", sessions)

        items = []
        for session in sessions:
            if "NowPlayingItem" not in session:
                continue

            now_playing = session["NowPlayingItem"]
            # session with NowPlayingItem, apply below fiter to get specific data only
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

            now_playing = filter_dict(now_playing, keys=filter_keys)
            if not now_playing:
                # looks like filter is broken its not wokring
                self.logger.error("Not able find any data from NowPlayingItem")
                continue

            self.logger.info("Currently playing: %s", now_playing["Name"])
            items.append(now_playing)

        return items
