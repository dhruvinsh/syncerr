"""
Author: Dhruvin Shah
Schema definition for the Plex.
"""

from datetime import datetime

from pydantic import BaseModel


class Detail(BaseModel):
    """
    MovieDetail data holder for Plex.
    It is purerly here just to mimic jellyfin API. Which in my opinion is good.
    """

    percentage: float
    playback_time: int
    play_count: int
    last_played: datetime
    played: bool
    key: str


class Movie(BaseModel):
    """
    Movie data holder Plex.
    {
      "ratingKey": "1",
      "key": "/library/metadata/1",
      "type": "movie",
      "title": "2 Fast 2 Furious",
      "duration": 6461793
    }

    mappings:
        name: title,
        id: ratingKey,
        run_time: duration
        category: movie
        details:
    """

    name: str
    id: str
    run_time: int
    category: str = "movie"
    details: Detail


class Series(BaseModel):
    """
    Series data holder for Jellyfin.

    {
      "ratingKey": "1498",
      "key": "/library/metadata/1498/children",
      "type": "show",
      "title": "Arcane",
      "index": 1,
      "duration": 2340000,
      "details": [
        {
          "ratingKey": "1499",
          "key": "/library/metadata/1499/children",
          "type": "season",
          "title": "Season 1",
          "index": 1,
          "episodes": [
            {
              "ratingKey": "1500",
              "key": "/library/metadata/1500",
              "type": "episode",
              "title": "Welcome to the Playground",
              "index": 1,
              "duration": 2605472
            }
          ]
        }
      ]
    }

    mappings:
        name: title
        id: ratingKey
        category: "series"
        seasons: list[Episode]
    """

    name: str
    id: str
    category: str = "series"
    seasons: list["Season"]


class Season(BaseModel):
    """
    Season data holder for Jellyfin.

    {
      "ratingKey": "1498",
      "key": "/library/metadata/1498/children",
      "type": "show",
      "title": "Arcane",
      "index": 1,
      "duration": 2340000,
      "details": [
        {
          "ratingKey": "1499",
          "key": "/library/metadata/1499/children",
          "type": "season",
          "title": "Season 1",
          "index": 1,
          "episodes": [
            {
              "ratingKey": "1500",
              "key": "/library/metadata/1500",
              "type": "episode",
              "title": "Welcome to the Playground",
              "index": 1,
              "duration": 2605472
            }
          ]
        }
      ]
    }

    mappings:
        name: title
        id: ratingKey
        index: index
        category: "season"
        episodes: list[Episode]
    """

    name: str
    id: str
    index: int
    category: str = "season"
    episodes: list["Episode"]


class Episode(BaseModel):
    """
    Episode data holder for Jellyfin.

    {
      "ratingKey": "1498",
      "key": "/library/metadata/1498/children",
      "type": "show",
      "title": "Arcane",
      "index": 1,
      "duration": 2340000,
      "details": [
        {
          "ratingKey": "1499",
          "key": "/library/metadata/1499/children",
          "type": "season",
          "title": "Season 1",
          "index": 1,
          "episodes": [
            {
              "ratingKey": "1500",
              "key": "/library/metadata/1500",
              "type": "episode",
              "title": "Welcome to the Playground",
              "index": 1,
              "duration": 2605472
            }
          ]
        }
      ]
    }

    mappings:
        name: title
        id: ratingKey
        run_time: duration
        index: index
        category: "episode"
    """

    name: str
    id: str
    run_time: int
    index: int
    category: str = "episode"
    details: Detail
