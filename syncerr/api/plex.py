"""
author: Dhruvin Shah
very minimal plex api that just works.
"""

from json.decoder import JSONDecodeError
from typing import Any, Union

import httpx

from syncerr.logger import create_logger
from syncerr.util import filter_dict


class Plex:
    """
    Minimal Plex api

    :param url: plex server url
    :param token: authentication token for the given plex server
    :param appname: app name to set when accessing plex instance, default to syncerr
    """

    def __init__(self, url: str, token: str, appname: str = "syncerr") -> None:
        self.url = url.rstrip("/")
        self.token = token
        self.appname = appname

        self.identifier = "com.plexapp.plugins.library"

        headers: dict[str, Any] = {
            "Accept": "application/json",  # if not set then xml gets return
            "X-Plex-Product": self.appname,
            "X-Plex-Platform": "syncerr-api",
            "X-Plex-Platform-Version": "1.0.0",
            "X-Plex-Device": "Syncerr",
            "X-Plex-Device-Name": "Syncerr",
            "X-Plex-Token": self.token,
            "X-Plex-Language": "en",
        }
        self.sess = httpx.Client(headers=headers)
        self.logger = create_logger(self.__class__.__name__)

    def _call(
        self,
        method: str,
        url: str,
        *,
        filter_keys: Union[list[str], dict[str, Any], None] = None,
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
        # plex by default return json data encapsulated withing MediaContainer
        try:
            res = resp.json().get("MediaContainer", {})
        except JSONDecodeError:
            self.logger.error("json decoding error")
            breakpoint()

        # TODO: figure out better way, this is ugly hack!!
        if filter_keys:
            if isinstance(filter_keys, dict):
                # need specific sub data
                for k in filter_keys.keys():
                    # should be just one key, else we will forcefull use one key
                    res = res.get(k, {})
                    keys = filter_keys[k]
                    break
            elif isinstance(filter_keys, list):
                # straight filter nothing needs to be done
                keys = filter_keys
        else:
            return res

        # if response is list of dicts then filter need to apply to each dict
        if isinstance(res, list):
            return list(map(lambda r: filter_dict(r, keys=keys), res))

        return filter_dict(res, keys)

    def library_types(self) -> list[dict[str, str]]:
        """
        Find numbers of library available in plex instance.
        NOTE: out of all, movie and shows required

        ENDPOINT: /library/sections/
        TYPE: GET
        PAYLOAD:
        RESPONSE: json

        :return: list
        [
            {...,
            'composite': '/library/sections/1/composite/1663926060',
            'key': '1',
            'title': 'Movies',
            'type': 'movie',
            'uuid': '39ee6e1e-7a1c-4abd-acb6-4e5a58cb6b73',
            'Location': {'id': ..
                        'path': ..}
            },
            ...
        ]
        """
        url = self.url + "/library/sections/"
        res = self._call("get", url)
        self.logger.debug(res)

        return res["Directory"]

    def items(self, lib_key: str):
        """
        Get all media items. For movie, there are no sub-data to be fetched, but in
        case of show child node need to be fetched.

        :param lib_key: library id (key) to use to fetch all the items

        ENDPOINT: /library/sections/<library_key>/all
        TYPE: GET
        PAYLOAD:
        RESPONSE:

        :return: dict
        """
        url = self.url + f"/library/sections/{lib_key}/all"
        params = {"type": lib_key}

        # we only need certain data out of "Metadata"
        filter_keys = {
            "Metadata": ["duration", "index", "key", "ratingKey", "title", "type"]
        }

        items = self._call("get", url, filter_keys=filter_keys, params=params)
        self.logger.debug(items)

        return items

    def traverse_child(self, lib_key: str) -> list[dict[str, Any]]:
        """
        In case of show we need to fetch child data,
        Show -> Seasons -> Episodes

        ENDPOINT: /library/metadata/{ratingKey}/children
        TYPE: GET
        PAYLOAD:
        RESPONSE:
        """
        url = self.url + f"/library/metadata/{lib_key}/children"
        filter_keys = {
            "Metadata": ["duration", "index", "key", "ratingKey", "title", "type"]
        }

        # fetch all the seasons
        seasons = self._call("get", url, filter_keys=filter_keys)

        # fetch all the episodes
        for season in seasons:
            url = self.url + f"/library/metadata/{season['ratingKey']}/children"
            episodes = self._call("get", url, filter_keys=filter_keys)
            season["episodes"] = episodes

        return seasons

    def mark_status(self, item: dict[str, Any], progress: float) -> None:
        """
        For given item mark the progress.
        Based on the progress it can be played, unpalyed or fractional percentage.

        :param item: plex media item with ratingKey, duration value

        ENDPOINT(s): /:/scrobble, /:/unscrobble
        TYPE: GET
        PAYLOAD: {"key": str, "identifier": str}
        RESPONSE:

            ENDPOINT(s): /:/progress
        TYPE: GET
        PAYLOAD: {"key": str, "identifier": str, time: int, state: "stopped"}
        RESPONSE:

        :return:
        """
        key = item["ratingKey"]
        ptime = int((item["duration"] * progress) / 100)

        match progress:
            case 0.0:
                url = self.url + "/:/unscrobble"
                params = {"key": key, "identifier": self.identifier}
            case 100.0:
                url = self.url + "/:/scrobble"
                params = {"key": key, "identifier": self.identifier}
            case _:
                url = self.url + "/:/progress"
                params = {
                    "key": key,
                    "identifier": self.identifier,
                    "time": ptime,
                    "state": "stopped",
                }

        resp = self.sess.get(url, params=params)

        match resp.status_code:
            case 200:
                self.logger.info(
                    "Successfully updated the satus of %s.", {item["title"]}
                )
            case 400 | 401 | 404:
                self.logger.error("Fail to udpate the status of %s.", {item["title"]})
