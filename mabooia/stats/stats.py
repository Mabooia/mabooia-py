import abc
from typing import Iterable

from mabooia.collections import Stream


class Countable(abc.ABC):

    @property
    @abc.abstractmethod
    def countable_value(self):
        pass


class Stat(abc.ABC):
    def __init__(self, value):
        self._value = value

    def __str__(self):
        return str(self.value)

    def __int__(self):
        return int(self.value)

    def __float__(self):
        return float(self.value)

    @property
    def value(self):
        return self._value

    @abc.abstractmethod
    def aggregate(self, other):
        pass


class Count(Stat):
    def __init__(self, value: float = 0):
        Stat.__init__(self, value)

    def aggregate(self, other):
        assert isinstance(other, Count)
        return Count(self.value + other.value)


def count(values: Iterable):
    res = Stream.of(values).fold(0, lambda acc, _: acc + 1)
    return Count(res)


class Sum(Stat):
    def __init__(self, value: float = 0):
        Stat.__init__(self, value)

    def aggregate(self, other):
        assert isinstance(other, Sum)
        return Sum(self.value + other.value)


def summation(values: Iterable):
    res = Stream.of(values).fold(0, lambda acc, v: acc + v)
    return Sum(res)


class Avg(Stat):
    def __init__(self, s: Sum, c: Count):
        Stat.__init__(self, s.value / c.value if c.value != 0 else 0)
        self._sum = s
        self._count = c

    def aggregate(self, other):
        assert isinstance(other, Avg)

        return Avg(
            self._sum.aggregate(other._sum),
            self._count.aggregate(other._count)
        )


def avg(values: Iterable):
    c = count(values)
    s = summation(values)
    return Avg(s, c)


class AllStat:

    @staticmethod
    def of(values: Iterable):
        c = count(values)
        s = summation(values)
        return AllStat(c, s)

    def __init__(self, c: Count = Count(), s: Sum = Sum()):
        self._count = c
        self._sum = s

    @property
    def count(self):
        return self._count

    @property
    def sum(self):
        return self._sum

    @property
    def avg(self):
        return Avg(self._sum, self._count)

    def aggregate(self, other):
        assert isinstance(other, AllStat)

        return AllStat(
            self._count.aggregate(other._count),
            self._sum.aggregate(other._sum)
        )
