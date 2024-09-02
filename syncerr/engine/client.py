"""HTTP Engine to make request to relevent API server."""

from typing import Any

import httpx
from pydantic import Json

from syncerr.util import filter_dict


class HttpEngine:
    """HTTP Engine to deal with rest API."""

    def __init__(self, **kwargs: Any) -> None:
        """Bootstrap the HttpEngine.

        :param kwargs: any parameters that applies to `httpx.Client`
        """
        self.session = httpx.Client(follow_redirects=True, **kwargs)

    def _call(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        """Generic call method for rest API.

        :param method: type of method for httpx session
        :param url: url to fetch/send data to
        :param kwargs: key arguments to send for httpx client
        """
        assert method in ["get", "post"]

        fetch = getattr(self.session, method)
        ret = fetch(url, **kwargs)

        match ret.status_code:
            case 200:
                return ret
            case _:
                raise httpx.RequestError(f"Not able to fetch data: {url}")

    def get(
        self, url: str, *, filter_keys: list[str] | None = None, **kwargs: Any
    ) -> Json[Any]:
        """General method to call url.

        It returns the json object and applies filter_keys to it befor that.

        :param url: endpoint that need to call
        :param filter_keys: for jsonified object applie filter to obtain certain keys
                            only
        :param kwargs: all the options that applies to rest call
        """
        resp = self._call("get", url, **kwargs)
        res = resp.json()

        if filter_keys is None:
            return res

        # if response is list of dicts then filter need to apply to each dict
        if isinstance(res, list):
            return [filter_dict(r, filter_keys) for r in res]

        return filter_dict(res, filter_keys)

    def post(self, url: str, json: Any | None = None) -> httpx.Response:
        """Send post request.

        :param url: pass url to make post request
        :param kwargs: all the key arguments passed to httpx client's post requests
        """
        return self._call("post", url, json=json)
