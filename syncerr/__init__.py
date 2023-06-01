"""
An application to sync jellyfin and plex currently playing also already played
media.
"""

from syncerr.api.jellyfin import Jellyfin, currently_playing
from syncerr.api.plex import Plex

__all__: list[str] = ["Jellyfin", "Plex", "currently_playing"]
__author__: str = "Dhruvin Shah<dhruvin3@gmail.com>"
__version__: str = "0.1.0"
