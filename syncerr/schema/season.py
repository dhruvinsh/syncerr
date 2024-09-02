"""Season schema for all type of media."""

from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from .episode import Episode


class Season(BaseModel):
    """Season data holder.

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
            name: SeasonName,
            id: SeasonId,
            index: ParentIndexNumber
            episodes: list[Episode]
            category: "season"

    For Plex,
    """

    name: str
    id: str
    index: int
    episodes: list["Episode"]
    category: str = "season"
