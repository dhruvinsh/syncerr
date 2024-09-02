"""Various data encpsulator."""

from pydantic import BaseModel


class NowPlayingData(BaseModel):
    """Data encpsulator for now playing.

    :param cid: content Id.
    :param ctype: content Type.
    """

    cid: str
    ctype: str
