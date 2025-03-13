"""Minimal Jellyfin api for syncerr.

This module provides a minimal API client for interacting with a Jellyfin server within
the syncerr ecosystem. It supports authentication via username and password, retrieval
of media details, and fetching of currently playing sessions.
"""

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

    This class implements a minimal API client for interacting with a Jellyfin media
    server. Currently, authentication is done via username and password for Jellyfin.
    It supports engine building, session authentication, and fetching media details.
    """

    CLIENT: str = "syncerr"
    DEVICE: str = "syncerr-api"
    # TODO: find a way to generate unique device id or pass as env
    DEVICE_ID: str = "4226af2e-a4fa-43e5-8d4c-f6a9f6de181e"
    VERSION: str = "1.0.0"

    def __init__(
        self, url: str, username: str, password: str, engine: type["HttpEngine"]
    ) -> None:
        """Initialize a new Jellyfin client instance.

        This constructor sets up the Jellyfin API client by storing the server URL,
        user credentials, and initializing the HTTP engine for subsequent API calls.
        It also ensures that the URL does not have a trailing slash and configures the
        engine with appropriate headers.

        Args:
            url (str): Jellyfin server URL.
            username (str): Jellyfin username.
            password (str): Jellyfin password.
            engine (type[HttpEngine]): An HTTP engine class used for making API
            requests.

        Note:
            The provided engine should support header configuration and REST API call
            methods.
        """
        self.url = url.rstrip("/")
        self.username = username
        self.password = password
        self.is_authenticated = False
        self.engine = self.build_engine(engine)

    def build_engine(self, engine: type["HttpEngine"]) -> "HttpEngine":
        """Build and configure the HTTP engine with the necessary headers.

        This method instantiates the provided HTTP engine with Jellyfin-specific headers
        for client identification, and then performs authentication to obtain an access
        token. The engine is subsequently updated with these credentials.

        Args:
            engine (type[HttpEngine]): The HTTP engine class used for making API
            requests.

        Returns:
            HttpEngine: A configured HTTP engine instance with updated authentication
            headers.
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
        """Get the authentication status.

        Returns:
            bool: True if the client is authenticated with the Jellyfin server, False
            otherwise.
        """
        return self._is_authenticated

    @is_authenticated.setter
    def is_authenticated(self, value: bool) -> None:
        assert value in [True, False]
        self._is_authenticated = value

    def authenticate(self, session: "HttpEngine") -> Json[Any] | None:
        """Authenticate the client against the Jellyfin server.

        This method performs authentication using the provided username and password.
        A POST request is sent to the /Users/authenticatebyname endpoint with a payload
        containing the credentials. Note that the API requires admin user privileges for
        complete access, and non-admin users might not be able to fully utilize the API.

        Args:
            session (HttpEngine): The HTTP engine instance used to make the request.

        Returns:
            dict | None: A JSON dictionary containing authentication details if the
            request is successful; otherwise, None is returned.

        Note:
            If authentication fails (HTTP status code is not 200), an error is logged.
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
        """Retrieve media details for a given item.

        This method sends a GET request to the Jellyfin API to fetch details for a
        specified media item. It calls the endpoint /Users/{userId}/Items/{item_id} and
        expects a JSON response containing information such as index numbers, names,
        paths, runtime, and user data.

        Args:
            item_id (str): The identifier of the media item for which details should be
            retrieved.

        Returns:
            Json[Any]: A JSON object containing the details of the media item.

        Note:
            The client must be authenticated before calling this method.
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
        """Retrieve a list of currently playing media items in JSON format.

        This method queries the /Sessions endpoint to obtain active media sessions
        within a specified time window.
        It filters the session data to extract only the media item IDs and types.

        Args:
            active_time (int, optional): Time in seconds to consider a session as active
            (default is 900 seconds).

        Returns:
            list: A list of JSON objects each representing a playing media item.

        Note:
            Specifying the 'activeWithinSeconds' parameter helps optimize the API
            response.
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
        """Fetch a list of recently played media items.

        This method retrieves media items (movies or episodes) that are actively playing
        or have been recently played, based on the specified time window.

        Args:
            active_time (int, optional): Time in seconds to consider a session as
            active. Defaults to 900 (15 minutes).

        Returns:
            list[Movie | Episode]: A list of media item objects representing movies or
            episodes.
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
        """Retrieve movie details.

        This method obtains detailed information about a movie by processing the user
        data from the now-playing media item. It calls the relevant Jellyfin endpoint
        to fetch supplementary information if required.

        Args:
            item_detail (NowPlayingData): JSON data representing the movie item,
            including user data.

        Returns:
            Movie: An instance of the Movie model with attributes such as name, runtime,
            and playback details.
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
        """Retrieve episode details.

        This method fetches detailed information for an episode by making a GET request
        to the Jellyfin API using the episode's ID as a parameter. It processes the
        returned user data to construct an Episode object.

        Args:
            item_detail (Json[Any]): JSON data representing the episode item, including
            user data.

        Returns:
            Episode: An instance of the Episode model with details such as name,
            runtime, index, and playback metrics.
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
