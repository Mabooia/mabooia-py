from typing import Callable


# Dictionary utils
from mabooia import Option, Some, Nothing


def put_if_absent(d: dict, key, value_if_absent):
    if key not in d.keys():
        d[key] = value_if_absent

    return d[key]


def compute_if_absent(d: dict, key, f: Callable):
    if key not in d.keys():
        d[key] = f()

    return d[key]


def get_value_option(d: dict, key) -> Option:
    if key in d.keys():
        return Some(d[key])

    return Nothing()
