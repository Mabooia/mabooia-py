import abc
from typing import *

from mabooia import Singleton, Option, Some, Nothing
from mabooia.collections.traversable import Traversable


class Stack(Traversable, abc.ABC):
    @staticmethod
    def of(collection):
        if collection is None:
            return EmptyStack()
        elif isinstance(collection, Stack):
            return collection
        elif isinstance(collection, Iterable):
            res = EmptyStack()
            for it in collection:
                res = res.push(it)
            return res
        else:
            raise TypeError(f"Cannot create a stack from {collection.__class__} type")

    def __str__(self):
        return f"Stack[{self._inner_str()}]"

    def push(self, value):
        return NonEmptyStack(value, self)

    def pop(self):
        return self.tail


class EmptyStack(Stack, Singleton):
    @property
    def head_option(self) -> Option:
        return Nothing()

    @property
    def tail(self):
        return self


class NonEmptyStack(Stack):
    def __init__(self, head, tail: Stack):
        self._head: Final = head
        self._tail: Final[Stack] = tail

    def peek(self):
        return self._head

    @property
    def head_option(self) -> Option:
        return Some(self.peek())

    @property
    def tail(self) -> Stack:
        return self._tail
