"""Detail schema for all type of media."""

from datetime import datetime

from pydantic import BaseModel


class Detail(BaseModel):
    """Detail data holder for Media.

    For Jellyfin's movies and episodes,
        Subset of Movie or Episode data,
            "UserData": {
                    "PlayedPercentage": float,
                    "PlaybackPositionTicks": int,
                    "PlayCount": int,
                    "LastPlayedDate": str(datetime),
                    "Played": bool,
                    "Key": str,
            },
        mappings:
            percentage: PlayedPercentage
            playback_time: PlaybackPositionTicks
            play_count: PlayCount
            last_played: LastPlayedDate
            played: Played
            key: Key

    For Plex's movies and episodes,
    """

    percentage: float
    playback_time: int
    play_count: int
    last_played: datetime
    played: bool
    key: str
