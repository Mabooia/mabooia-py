import abc
from calendar import monthrange
from datetime import datetime, date
from typing import Iterable, Union

from mabooia import Some
from mabooia.stats import AllStat
from mabooia.reactive import Observable, Observer
from mabooia.collections import Stream
from mabooia.collections.mutable import LinkedList


class TimelineEvent(abc.ABC):
    def __init__(self, dt: Union[datetime, date], info):
        self._datetime = dt
        self._info = info

    @property
    def datetime(self):
        return self._datetime

    @property
    def info(self):
        return self._info

    @property
    @abc.abstractmethod
    def stat_value(self):
        pass


class Timeline(Observer):
    def __init__(self):
        self._events = LinkedList()
        self._years = []

    @property
    def years(self):
        return self._years

    def add_event(self, event: TimelineEvent):
        self._events.append(event)
        year = event.datetime.year
        year_opt = Stream.of(self._years)\
            .filter(lambda y: int(y) == year)\
            .head_option

        year_obj: Year = year_opt.value if isinstance(year_opt, Some) else None
        if year_obj is None:
            year_obj = Year(year)
            year_obj.subscribe(self)
            self._years.append(year_obj)

        year_obj.add_event(event)

    def notify(self, year=None):
        if year is not None:
            year.refresh_invalid()


class TimeAgg(abc.ABC):
    def __init__(self, value: int, parent):
        self._value = value
        self._parent = parent
        self._all_stat = None

    def __int__(self):
        return self._value

    def __str__(self):
        return str(self._value)

    @property
    def all_stat(self):
        return self._all_stat

    def invalidate(self):
        self._all_stat = None
        if self.parent is not None:
            self.parent.invalidate()

    @abc.abstractmethod
    def add_event(self, ev: TimelineEvent):
        pass

    @abc.abstractmethod
    def refresh_invalid(self):
        pass

    @property
    def parent(self):
        return self._parent

    def _refresh_from_children(self, children: Iterable):
        if self._all_stat is None:
            self._all_stat = Stream.of(children)\
                .filter(lambda child: child is not None)\
                .for_each(lambda child: child.refresh_invalid())\
                .map(lambda child: child.all_stat)\
                .fold(AllStat(), lambda acc, it: acc.aggregate(it))


class Year(Observable, TimeAgg):
    def __init__(self, value: int):
        TimeAgg.__init__(self, value, None)
        self._months = [None] * 12

    @property
    def months(self):
        return Stream.of(self._months).filter(lambda m: m is not None)

    def quarter(self, n: int):
        assert 1 <= n <= 4

        _from = n - 1
        _to = _from + 2

        return Quarter(n, self)

    def month(self, n: int):
        return self._months[n - 1]

    def add_event(self, ev: TimelineEvent):
        idx = ev.datetime.month - 1

        m = self._months[idx]
        if m is None:
            m = self._months[idx] = Month(idx + 1, self)

        m.add_event(ev)

    def invalidate(self):
        TimeAgg.invalidate(self)
        self.notify_all(self)

    def refresh_invalid(self):
        self._refresh_from_children(self.months)


class Month(TimeAgg):
    def __init__(self, value, year: Year):
        TimeAgg.__init__(self, value, year)
        self._days = [None] * monthrange(int(self.year), int(self))[1]

    def __str__(self):
        v = int(self)
        v_str = str(v) if v >= 10 else f"0{v}"
        return f"{self.year}-{v_str}"

    @property
    def year(self):
        return self.parent

    @property
    def quarter(self):
        q = (int(self) - 1) / 3 + 1
        return self.year.quarter(q)

    @property
    def days(self):
        return Stream.of(self._days).filter(lambda d: d is not None)

    def add_event(self, ev: TimelineEvent):
        idx = ev.datetime.day - 1

        d = self._days[idx]
        if d is None:
            d = self._days[idx] = Day(idx + 1, self)

        d.add_event(ev)

    def refresh_invalid(self):
        self._refresh_from_children(self.days)


class Quarter(TimeAgg):
    def __init__(self, value, year: Year):
        TimeAgg.__init__(self, value, year)

    def __str__(self):
        return f"Q{int(self)}"

    @property
    def year(self):
        return self.parent

    def add_event(self, ev: TimelineEvent):
        pass

    def refresh_invalid(self):
        pass


class Day(TimeAgg):
    def __init__(self, value, month: Month):
        TimeAgg.__init__(self, value, month)
        self._events = LinkedList()

    def __str__(self):
        v = int(self)
        v_str = str(v) if v >= 10 else f"0{v}"
        return f"{self.month}-{v_str}"

    @property
    def year(self):
        return self.month.year

    @property
    def quarter(self):
        return self.month.quarter

    @property
    def month(self):
        return self.parent

    @property
    def events(self):
        return self._events.to_list()

    def add_event(self, ev: TimelineEvent):
        self._events.append(ev)
        self.invalidate()

    def refresh_invalid(self):
        if self._all_stat is None:
            values = Stream.of(self._events).map(lambda ev: ev.stat_value)
            self._all_stat = AllStat.of(values)
