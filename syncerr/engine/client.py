"""
HTTP Engine to make request to relevent API server
"""

import httpx
from pydantic import Json

from syncerr.util import filter_dict


class HttpEngine:
    """
    HTTP Engine to deal with rest API

    :param kwargs: any parameters that applies to `httpx.Client`
    """

    def __init__(self, **kwargs) -> None:
        self.session = httpx.Client(follow_redirects=True, **kwargs)

    def _call(self, method: str, url: str, **kwargs) -> httpx.Response:
        """
        generic call method for rest API

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

    def get(self, url: str, *, filter_keys: list[str] = [], **kwargs) -> Json:
        """
        General method to call url. It returns the json object and applies filter_keys
        to it befor that.

        :param url: endpoint that need to call
        :param filter_keys: for jsonified object applie filter to obtain certain keys
                            only
        :param kwargs: all the options that applies to rest call
        """
        resp = self._call("get", url, **kwargs)
        res = resp.json()

        if not filter_keys:
            return res

        # if response is list of dicts then filter need to apply to each dict
        if isinstance(res, list):
            return list(map(lambda r: filter_dict(r, keys=filter_keys), res))

        return filter_dict(res, filter_keys)

    def post(self, url: str, **kwargs) -> httpx.Response:
        """
        :param url: pass url to make post request
        :param kwargs: all the key arguments passed to httpx client's post requests
        """
        return self._call("post", url, **kwargs)
