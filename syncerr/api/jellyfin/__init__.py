"""
Jellyfin API with schema
"""

from .jellyfin import Jellyfin, currently_playing

__all__: list[str] = ["Jellyfin", "currently_playing"]
