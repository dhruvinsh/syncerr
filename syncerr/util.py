"""
Some utility functions
"""

from typing import Any, Optional


def filter_dict(dikt: dict[Any, Any], keys: Optional[list[str]] =None):
    """
    For given dict keep data ony with given values

    :param dikt: dict object that require some filtering
    :param keys: values of keys that need to keep
    """
    return {k: v for k, v in dikt.items() if k in keys}
