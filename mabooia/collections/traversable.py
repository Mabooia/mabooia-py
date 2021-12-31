import abc
from typing import *
import sys

from mabooia import Option, Nothing, Some
from mabooia.collections.mutable import LinkedList


class Traversable(Iterable, Sized, abc.ABC):

    def __iter__(self):
        class Iter(Iterator):
            def __init__(self, trav):
                self._trav = trav

            def __next__(self):
                head = self._trav.head_option
                if isinstance(head, Some):
                    self._trav = self._trav.tail
                    return head.value

                raise StopIteration

        return Iter(self)

    def __len__(self):
        res = 0
        for _ in self:
            res += 1
        return res

    @property
    @abc.abstractmethod
    def head_option(self) -> Option:
        raise NotImplementedError()

    @property
    def rear_option(self) -> Option:
        return self.fold(Nothing(), lambda _, it: Some(it))

    @property
    @abc.abstractmethod
    def tail(self):
        raise NotImplementedError()

    @property
    def is_empty(self) -> bool:
        return self.head_option.is_empty()

    @property
    def is_not_empty(self) -> bool:
        return not self.is_empty

    def corresponds(self,
                    other,
                    f: Callable = lambda a, b: a == b,
                    is_true: bool = True) -> bool:
        assert isinstance(other, Iterable)
        t1 = iter(self)
        t2 = iter(other)

        try:
            h1 = next(t1)
            h2 = next(t2)

            if f(h1, h2) != is_true:
                return False

        except StopIteration as _:
            pass

        return True

    def fold(self, initial_value, f2: Callable):
        res = initial_value
        for it in self:
            res = f2(res, it)

        return res

    def fold_while(self,
                   initial_value,
                   p2: Callable,
                   f2: Callable,
                   is_true: bool = True):
        res = initial_value
        for it in self:
            if p2(res, it) != is_true:
                break

            res = f2(res, it)

        return res

    def fold_while_indexed(self,
                           initial_value,
                           p3: Callable,
                           f3: Callable,
                           is_true: bool = True):
        res = initial_value
        idx = 0
        for it in self:
            if p3(res, it, idx) != is_true:
                break

            res = f3(res, it, idx)
            idx += 1

        return res

    def for_each(self, f: Callable):
        for it in self:
            f(it)

        return self

    def for_each_indexed(self, f2: Callable):
        idx = 0
        for it in self:
            f2(it, idx)
            idx += 1

        return self

    def for_each_while(self, p: Callable, f: Callable, is_true: bool = True):
        for it in self:
            if p(it) != is_true:
                break

            f(it)

        return self

    def for_each_while_indexed(self, p2: Callable, f2: Callable, is_true: bool = True):
        idx = 0
        for it in self:
            if p2(it, idx) != is_true:
                break

            f2(it, idx)
            idx += 1

        return self

    def to_list(self, max_size: int = sys.maxsize) -> list:
        size = min(len(self), max_size)
        res = [None] * size

        idx = 0
        for it in self:
            if idx >= size:
                break

            res[idx] = it
            idx += 1

        return res

    def _inner_str(self) -> str:
        return self._inner_str_max_length(", ", 256)

    def _inner_str_max_items(self, separator=", ", max_items=sys.maxsize) -> str:
        return self._inner_str_while(lambda acc, it, idx: idx < max_items, separator)

    def _inner_str_max_length(self, separator=", ", max_length=sys.maxsize) -> str:
        return self._inner_str_while(lambda acc, it, _: acc + len(str(it)) < max_length, separator)

    def _inner_str_while(self, p3: Callable, separator=", ") -> str:
        interrupted = dict()
        interrupted["value"] = False
        sb = LinkedList()

        def predicate(acc_length, it, idx):
            res = p3(acc_length, it, idx)
            if not res:
                interrupted["value"] = True

            return res

        def add_str(acc_length, it):
            it_str = str(it)
            sb.append(it_str)
            return acc_length + len(it_str)

        self.fold_while_indexed(
            0,
            predicate,
            lambda acc_length, it, idx: add_str(acc_length, it)
        )

        if interrupted["value"]:
            sb.append("...")

        return separator.join(sb)
