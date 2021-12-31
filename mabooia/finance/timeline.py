import abc
from calendar import monthrange
from datetime import datetime, date
from enum import Enum
from typing import Iterable, Union, Callable

from mabooia.collections import Stream, LinkedList


class TimelineEvent:
    def __init__(self, _date: date, _info):
        self._date = _date
        self._info = _info

    def __str__(self):
        return f"Event: {self.info} at {self.date}"

    @property
    def date(self):
        return self._date

    @property
    def info(self):
        return self._info


class TimelineRange(abc.ABC):
    def __init__(self, initial_agg_value, agg_func: Callable, parent=None):
        self._parent = parent
        self._initial_agg_value = initial_agg_value
        self._agg_func = agg_func
        self._agg_value = None

    @property
    def parent(self):
        return self._parent

    @property
    def agg_value(self):
        if self._agg_value is None:
            self._agg_value = self.events.fold(self._initial_agg_value, self._agg_func)

        return self._agg_value

    def invalidate(self):
        self._agg_value = None
        if isinstance(self.parent, TimelineRange):
            self.parent.invalidate()

    @property
    @abc.abstractmethod
    def events(self) -> Stream:
        pass

    @abc.abstractmethod
    def add_event(self, event: TimelineEvent):
        pass


class DayOfMonthRange(TimelineRange):
    def __init__(self, initial_agg_value, agg_func: Callable, parent, day_of_month: int):
        TimelineRange.__init__(self, initial_agg_value, agg_func, parent)
        self._day_of_month = day_of_month
        self._events = LinkedList()

    @property
    def events(self) -> Stream:
        return Stream.of(self._events)

    def add_event(self, event: TimelineEvent):
        self._events.append(event)
        self.invalidate()


class MonthRange(TimelineRange):
    def __init__(self, initial_agg_value, agg_func: Callable, parent, month: int):
        TimelineRange.__init__(self, initial_agg_value, agg_func, parent)
        self._month = month


class Timeline:
    class _TimelineEventNode(TimelineEvent):
        def __init__(self, _date: date, _info, _prev, _next):
            TimelineEvent.__init__(self, _date, _info)
            self.prev = _prev
            self.next = _next

    class _TimelineRangeType(Enum):
        UNKNOWN = 0
        YEAR = 1
        QUARTER = 2
        MONTH = 3
        WEEK = 4
        DAY = 5

        def __str__(self):
            return self.name

    def __init__(self):
        null_date = date(0, 0, 0)
        self._head = self._TimelineEventNode(null_date, None, None, None)
        self._rear = self._TimelineEventNode(null_date, None, None, None)
        self._head.next = self._rear
        self._rear.prev = self._head
        self._years = dict()
