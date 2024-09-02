"""Series schema for all type of media."""

from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from .season import Season


class Series(BaseModel):
    """Series data holder.

    For Jellyfin,
        {
            "Name": str,
            "Id": str,
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
            name: SeriesName,
            id: SeriesId,
            category: "series"
            seasons: list[Season]

    For Plex,
    """

    name: str
    id: str
    seasons: list["Season"]
    category: str = "series"
