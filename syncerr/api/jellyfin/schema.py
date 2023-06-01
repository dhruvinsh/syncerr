"""
Author: Dhruvin Shah
Schema definition for the Jellyfin.
"""

from datetime import datetime

from pydantic import BaseModel


class Detail(BaseModel):
    """
    Detail data holder for Jellyfin's movies and episodes.

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

    """

    percentage: float
    playback_time: int
    play_count: int
    last_played: datetime
    played: bool
    key: str


class Movie(BaseModel):
    """
    Movie data holder Jellyfin.

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
        id: Id,
        run_time: RunTimeTicks,
        details: Detail
        category: "movie"
    """

    name: str
    id: str
    run_time: int
    details: Detail
    category: str = "movie"


class Series(BaseModel):
    """
    Series data holder for Jellyfin.

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
    """

    name: str
    id: str
    seasons: list["Season"]
    category: str = "series"


class Season(BaseModel):
    """
    Season data holder for Jellyfin.

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
    """

    name: str
    id: str
    index: int
    episodes: list["Episode"]
    category: str = "season"


class Episode(BaseModel):
    """
    Episode data holder for Jellyfin.

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
    """

    name: str
    id: str
    run_time: int
    index: int
    details: Detail
    category: str = "episode"
