import hashlib
from typing import Iterable, Callable

from mabooia.collections import Stream, LinkedList


def bin_to_hex(_iterable: Iterable, upper: bool = False) -> str:
    _format = "%0.2X" if upper else "%0.2x"

    res = LinkedList()
    for b in _iterable:
        res.append(_format % b)

    return ''.join(res)


def hash_of(_iterable: Iterable, hash_alg):
    for b in _iterable:
        hash_alg.update(b)

    return hash_alg.digest()


def sha256(_iterable: Iterable):
    return hash_of(_iterable, hashlib.sha256())


def sha512(_iterable: Iterable):
    return hash_of(_iterable, hashlib.sha512())


def sha256_to_str(_iterable: Iterable, to_format_func: Callable = bin_to_hex) -> str:
    binaries = Stream\
        .of(_iterable)\
        .map(lambda s: s.encode('utf-8'))

    hs = sha256(binaries)
    return to_format_func(hs)
