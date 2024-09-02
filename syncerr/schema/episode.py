"""Episode schema for all type of media."""
from pydantic import BaseModel

from .detail import Detail


class Episode(BaseModel):
    """Episode data holder.

    For Jellyfin,
        {
            "Name": str,
            "Id": str,
            "SortName": str,
            "Path": str,
            "RunTimeTicks": int,
            "IndexNumber": int,
            "ParentIndexNumber": int,
            "Type": str,
            "UserData": {
                "PlayedPercentage": float,
                "PlaybackPositionTicks": int,
                "PlayCount": int,
                "IsFavorite": bool,
                "LastPlayedDate": str(datetime),
                "Played": bool,
                "Key": str,
            },
            "SeriesName": str,
            "SeriesId": str,
            "SeasonId": str,
            "SeasonName": str,
        }

        mappings:
            name: Name,
            id: Id,
            run_time: RunTimeTicks,
            index: IndexNumber
            details: Detail
            category: "episode"

    For Plex,
    """

    name: str
    id: str
    run_time: int
    index: int
    details: Detail
    category: str = "episode"
