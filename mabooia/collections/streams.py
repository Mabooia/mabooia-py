import abc
from typing import *

from mabooia import Singleton, Option, Some, Nothing, lazy, Lazy
from mabooia.collections import Traversable, Stack


class Stream(Traversable, abc.ABC):

    @staticmethod
    def of(_iterable: Iterable):
        if _iterable is None:
            return EmptyStream()
        elif isinstance(_iterable, Stream):
            return _iterable
        elif isinstance(_iterable, list):
            res = EmptyStream()
            for idx in range(len(_iterable) - 1, -1, -1):
                res = ConsStream(_iterable[idx], res)
            return res

        return Stack\
            .of(_iterable)\
            .fold(EmptyStream(), lambda acc, it: ConsStream(it, acc))

    def __str__(self):
        return f"Stream[{self._inner_str()}]"

    def all(self, f: Callable, is_true: bool = True) -> bool:
        curr = self
        curr_head = curr.head_option
        while isinstance(curr_head, Some):
            if f(curr_head.value) != is_true:
                return False
            curr = curr.tail
            curr_head = curr.head_option

        return True

    def append(self, item):
        return self\
            .head_option\
            .map(lambda head: LazyTailStream(head, lambda: self.tail.append(item)))\
            .get_or_else(SingleStream(item))

    def append_stream(self, stream):
        return self\
            .head_option\
            .map(lambda head: LazyTailStream(head, lambda: self.tail.append_stream(stream)))\
            .get_or_else(stream)

    def exists(self, f: Callable, is_true: bool = True) -> bool:
        return self\
            .filter(f, is_true)\
            .is_not_empty

    def filter(self, f: Callable, is_true: bool = True):
        def get_stream():
            filtered_to_head = self.skip_while(f, not is_true)

            def filter_tail():
                return filtered_to_head.tail.filter(f, is_true)

            return filtered_to_head\
                .head_option\
                .map(lambda head: LazyTailStream(head, filter_tail))\
                .get_or_else(EmptyStream())

        return LazyStream(get_stream)

    def flatmap(self, f: Callable):
        def get_stream():
            def prepend_head(head):
                new_head = f(head)

                if isinstance(new_head, Stream):
                    return new_head.append_stream(self.tail.flatmap(f))
                elif isinstance(new_head, Some):
                    return LazyTailStream(new_head.value, lambda: self.tail.flatmap(f))
                elif isinstance(new_head, Nothing):
                    return self.tail.flatmap(f)
                else:
                    raise TypeError

            return self\
                .head_option\
                .map(prepend_head)\
                .get_or_else(EmptyStream())

        return LazyStream(get_stream)

    def flatten(self):
        return self.flatmap(lambda it: it)

    def group_by(self, f: Callable) -> dict:
        res = dict()

        for it in self:
            key = f(it)
            if key in res.keys():
                res[key].append(it)
            else:
                res[key] = [it]

        return res

    def index_of(self, item) -> int:
        idx = 0
        curr = self
        curr_head = curr.head_option
        while isinstance(curr_head, Some):
            if curr_head.value == item:
                return idx

            idx += 1
            curr = curr.tail
            curr_head = curr.head_option

        return -1

    def map(self, f: Callable):
        def get_stream():
            return self\
                .head_option\
                .map(lambda head: LazyTailStream(f(head), lambda: self.tail.map(f)))\
                .get_or_else(EmptyStream())

        return LazyStream(get_stream)

    def map_indexed(self, f2: Callable):
        def get_stream(stream, idx):
            return stream\
                .head_option\
                .map(lambda head: LazyTailStream(f2(head, idx), lambda: get_stream(stream.tail, idx + 1)))\
                .get_or_else(EmptyStream())

        return LazyStream(lambda: get_stream(self, 0))

    def prepend(self, head):
        if self.is_empty:
            return SingleStream(head)

        return ConsStream(head, self)

    def prepend_stream(self, head_stream):
        return head_stream.append_stream(self)

    def slice(self, size: int):
        assert size > 0

        def get_stream(stream):
            if stream.is_empty:
                return stream

            page = [None] * size

            idx = 0
            curr = stream
            curr_head = curr.head_option
            while idx < size and isinstance(curr_head, Some):
                page[idx] = curr_head.value
                idx += 1
                curr = curr.tail
                curr_head = curr.head_option

            return LazyTailStream(page[:idx], lambda: get_stream(curr))

        return LazyStream(lambda: get_stream(self))

    def skip(self, count: int):
        return self.skip_while_indexed(lambda _, idx: idx < count)

    def skip_while(self, f: Callable, is_true: bool = True):
        def get_stream():
            curr = self
            curr_head = curr.head_option
            while isinstance(curr_head, Some) and f(curr_head.value) == is_true:
                curr = curr.tail
                curr_head = curr.head_option

            return curr

        return LazyStream(get_stream)

    def skip_while_indexed(self, f2: Callable, is_true: bool = True):
        def get_stream():
            curr = self
            curr_head = curr.head_option
            idx = 0
            while isinstance(curr_head, Some) and f2(curr_head.value, idx) == is_true:
                curr = curr.tail
                curr_head = curr.head_option
                idx += 1

            return curr

        return LazyStream(get_stream)

    def take(self, count: int):
        return self.take_while_indexed(lambda _, idx: idx < count)

    def take_while(self, f: Callable, is_true: bool = True):
        def get_stream(stream):
            return stream\
                .head_option\
                .filter(lambda head: f(head) == is_true)\
                .map(lambda head: LazyTailStream(head, lambda: get_stream(stream.tail)))\
                .get_or_else(EmptyStream())

        return LazyStream(lambda: get_stream(self))

    def take_while_indexed(self, f2: Callable, is_true: bool = True):
        def get_stream(stream, idx):
            return stream\
                .head_option\
                .filter(lambda head: f2(head, idx) == is_true)\
                .map(lambda head: LazyTailStream(head, lambda: get_stream(stream.tail, idx + 1)))\
                .get_or_else(EmptyStream())

        return LazyStream(lambda: get_stream(self, 0))

    def unzip(self, f: Callable):
        stream = self.map(f)
        return (
            stream.map(lambda it: it[0]),
            stream.map(lambda it: it[1])
        )

    def zip(self, other):
        def get_stream(stream_a, stream_b):
            head_a = stream_a.head_option
            if not isinstance(head_a, Some):
                return EmptyStream()

            head_b = stream_b.head_option
            if not isinstance(head_b, Some):
                return EmptyStream()

            return LazyTailStream(
                (head_a.value, head_b.value),
                lambda: get_stream(stream_a.tail, stream_b.tail)
            )

        return LazyStream(lambda: get_stream(self, other))


class EmptyStream(Stream, Singleton):

    @property
    def head_option(self) -> Option:
        return Nothing()

    @property
    def tail(self):
        return self


class NonEmptyStream(Stream, abc.ABC):

    def __init__(self, head):
        self.head: Final = head

    @property
    def rear(self):
        return self.fold(self.head, lambda _, it: it)

    @property
    def head_option(self) -> Option:
        return Some(self.head)


class SingleStream(NonEmptyStream):

    def __init__(self, head):
        NonEmptyStream.__init__(self, head)

    @property
    def tail(self):
        return EmptyStream()


class ConsStream(NonEmptyStream):

    def __init__(self, head, tail: Stream):
        NonEmptyStream.__init__(self, head)
        self._tail: Final[Stream] = tail

    @property
    def tail(self):
        return self._tail


class LazyTailStream(NonEmptyStream):

    def __init__(self, head, lazy_tail: Lazy | Callable):
        NonEmptyStream.__init__(self, head)
        self._lazy_tail: Final[Lazy] = lazy(lazy_tail)

    def __len__(self):
        return 1 + len(self._lazy_tail.get())

    @property
    def tail(self):
        return self._lazy_tail.get()

    def _inner_str(self):
        if self._lazy_tail.is_computed():
            return f"{self.head}, {Stream._inner_str(self)}"

        return f"{self.head}, ..."


class LazyStream(Stream):

    def __init__(self, lazy_stream: Lazy | Callable):
        self._lazy_stream: Final[Lazy] = lazy(lazy_stream)

    def __len__(self):
        return len(self._lazy_stream.get())

    def __eq__(self, other):
        if isinstance(other, LazyStream):
            return self._lazy_stream.get() == other._lazy_stream.get()
        elif isinstance(other, Stream):
            return self._lazy_stream.get() == other

        return False

    @property
    def head_option(self) -> Option:
        return self.touch().head_option

    @property
    def tail(self):
        return self.touch().tail

    def touch(self):
        lazy_stream = self._lazy_stream.get()
        while isinstance(lazy_stream, LazyStream):
            lazy_stream = lazy_stream._lazy_stream.get()

        return lazy_stream

    def _inner_str(self):
        if self._lazy_stream.is_computed():
            return Stream._inner_str(self)

        return "..."
