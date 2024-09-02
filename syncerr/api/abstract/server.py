"""Common abstract class for server implementations.

Currently applicable for Jellyfin and Plex.
"""

from abc import ABC, abstractmethod


class ServerAbstract(ABC):
    """Common abstract for Jellyfin and Plex server."""

    def __init__(self) -> None:
        """Constructor."""
        raise NotImplementedError

    @property
    @abstractmethod
    def is_authenticated(self) -> bool:
        """Check if server is authenticated."""
        raise NotImplementedError

    @is_authenticated.setter
    @abstractmethod
    def is_authenticated(self, value: bool) -> None:
        """Set server authentication status."""
        raise NotImplementedError

    @abstractmethod
    def authenticate(self) -> None:
        """Authenticate server."""
        raise NotImplementedError
