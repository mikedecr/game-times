from typing import Any

__all__ = ["only"]


def only(iterable) -> Any:
    """Return the only element of an iterable collection"""
    it = iter(iterable)
    try:
        value = next(it)
    except StopIteration:
        raise ValueError("No elements in collection")
    try:
        next(it)
    except StopIteration:
        return value
    raise ValueError("Multiple elements in collection")
