"""Movie schema for all type of media."""

from pydantic import BaseModel

from .detail import Detail


class Movie(BaseModel):
    """Movie data holder Jellyfin.

    Merging currently playing and get details get below data.
    {
        "Name": str,
        "Id": str,
        "SortName": str,
        "Path": str,
        "ParentId": str,
        "RunTimeTicks": int,
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
    }

    mappings:
        name: Name,
        item_id: Id,
        run_time: RunTimeTicks,
        details: Detail
        category: "movie"
    """

    name: str
    item_id: str
    run_time: int
    details: Detail
    category: str = "movie"
