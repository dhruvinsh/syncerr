"""
Some utility functions
"""

from typing import Any, Optional

from syncerr.logger import logger


def filter_dict(
    dikt: dict[Any, Any], keys: Optional[list[str]] = None
) -> dict[str, Any]:
    """
    For given dict keep data ony with given values

    :param dikt: dict object that require some filtering
    :param keys: values of keys that need to keep
    """
    if keys is None:
        logger.warning("filter keys not provided, set the filter keys")
        return dikt

    return {k: v for k, v in dikt.items() if k in keys}
