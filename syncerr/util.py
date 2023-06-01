"""
Some utility functions
"""

import logging
from typing import Any, Optional

from pydantic import Json


def filter_dict(dikt: dict[Any, Any], keys: Optional[list[str]] = None) -> Json:
    """
    For given dict drop all the keys except the one provided as keys

    :param dikt: dict object that require some filtering
    :param keys: values of keys that need to keep
    """
    if keys is None:
        logging.warning("filter keys not provided, set the filter keys")
        return dikt

    return {k: v for k, v in dikt.items() if k in keys}
