import abc
from calendar import monthrange
from datetime import date
from typing import Union, Callable

from mabooia import Some
from mabooia.collections import Stream, EmptyStream, LazyTailStream


# Timeline events
from mabooia.reactive import Observable


class TimelineEvent:
    def __init__(self, _date: date, _info):
        self._date = _date
        self._info = _info

    def __eq__(self, other):
        return isinstance(other, TimelineEvent) and self.date == other.date and self.info == other.info

    def __str__(self):
        return f"Event: {self.info} at {self.date}"

    @property
    def date(self):
        return self._date

    @property
    def info(self):
        return self._info


class _TimelineEventNode(TimelineEvent):
    def __init__(self, _date: date, _info, _prev, _next):
        TimelineEvent.__init__(self, _date, _info)
        self.prev = _prev
        self.next = _next

    def __str__(self):
        if self.is_head:
            return 'HEAD >>'

        if self.is_rear:
            return '<< REAR'

        return super(_TimelineEventNode, self).__str__()

    @property
    def is_head(self):
        return self.prev is None

    @property
    def is_rear(self):
        return self.next is None


# Search criteria

class TimeCriteria:
    def __init__(self, from_year=None, from_month=None, from_day=None, to_year=None, to_month=None, to_day=None):
        if from_year is not None and from_month is None:
            from_month = 1

        if from_month is not None and from_day is None:
            from_day = 1

        if to_year is not None and to_month is None:
            to_month = 12

        if to_month is not None and to_day is None:
            to_day = _get_month_count_of_days(to_year, to_month)

        self._from_year = from_year
        self._from_month = from_month
        self._from_day = from_day
        self._to_year = to_year
        self._to_month = to_month
        self._to_day = to_day

    @property
    def from_year(self):
        return self._from_year

    @property
    def from_month(self):
        return self._from_month

    @property
    def from_day(self):
        return self._from_day

    @property
    def to_year(self):
        return self._to_year

    @property
    def to_month(self):
        return self._to_month

    @property
    def to_day(self):
        return self._to_day


def all_events():
    return TimeCriteria()


def in_date(year, month=None, day=None):
    return TimeCriteria(
        from_year=year,
        from_month=month,
        from_day=day,
        to_year=year,
        to_month=month,
        to_day=day
    )


def since(year, month=None, day=None):
    return TimeCriteria(
        from_year=year,
        from_month=month,
        from_day=day
    )


def until(year, month=None, day=None):
    return TimeCriteria(
        to_year=year,
        to_month=month,
        to_day=day
    )


def in_range(from_year, from_month=None, from_day=None, to_year=None, to_month=None, to_day=None):
    return TimeCriteria(
        from_year=from_year,
        from_month=from_month,
        from_day=from_day,
        to_year=to_year,
        to_month=to_month,
        to_day=to_day
    )


# Timeline

class Timeline(Observable):

    def __init__(self):
        self._head = _TimelineEventNode(date.min, None, None, None)
        self._rear = _TimelineEventNode(date.max, None, None, None)
        self._head.next = self._rear
        self._rear.prev = self._head
        self._years = []

    def events(self, criteria: TimeCriteria = all_events()) -> Stream:
        offset = self._find_offset(criteria.from_year, criteria.from_month, criteria.from_day)

        def condition(event: TimelineEvent) -> bool:
            y = criteria.to_year
            if y is None:
                return True
            else:
                m = criteria.to_month if criteria.to_month is not None else 12
                d = criteria.to_day if criteria.to_day is not None else _get_month_count_of_days(y, m)

                criteria_date = date(y, m, d)
                return event.date <= criteria_date

        return self._get_events_from(offset, condition)

    def add_event(self, event: TimelineEvent):
        dt = event.date
        offset = self._find_offset(dt.year, dt.month, dt.day)
        next_node = self._find_position(event.date, offset if offset is not None else self._rear)
        new_node = _TimelineEventNode(event.date, event.info, next_node.prev, next_node)
        new_node.prev.next = new_node
        new_node.next.prev = new_node
        
        self._index_node(new_node)
        self.notify_all(event)
        return self

    def _find_position(self, dt: date, offset: _TimelineEventNode = None) -> _TimelineEventNode:
        curr = offset if offset is not None else self._head

        while curr.date <= dt and curr != self._rear:
            curr = curr.next

        return curr

    def _find_offset(self, year: int, month: int = None, day: int = None) -> Union[_TimelineEventNode, None]:
        years = Stream\
            .of(self._years)\
            .filter(lambda yix: year is None or yix.value >= year)

        year_index = None
        curr = years
        curr_head = curr.head_option
        while year_index is None and isinstance(curr_head, Some):
            year_index = curr_head.value
            curr = curr.tail
            curr_head = curr.head_option

        if year_index is not None:
            if year == year_index.value:
                return year_index.get_first(month, day)
            else:
                return year_index.get_first()

        return None
    
    def _get_events_from(self, offset: _TimelineEventNode, cond: Callable) -> Stream:
        if offset is None:
            offset = self._head.next

        if offset == self._rear or not cond(offset):
            return EmptyStream()
        
        return LazyTailStream(offset, lambda: self._get_events_from(offset.next, cond))
    
    def _index_node(self, node: _TimelineEventNode):
        year = node.date.year
        yix = _YearIndex(year)

        found_opt = Stream\
            .of(self._years)\
            .filter(lambda y: y.value == year)\
            .head_option

        if isinstance(found_opt, Some):
            yix = found_opt.value
        else:
            self._years.append(yix)
            self._years.sort(key=lambda y: y.value)

        yix.re_index(node)


# Indexes

class _Index(abc.ABC):

    offset: _TimelineEventNode = None

    def __init__(self, value: int):
        self._value = value

    @property
    def value(self):
        return self._value

    def re_index(self, node: _TimelineEventNode):
        if self.offset is None or node.date < self.offset.date:
            self.offset = node

        self._re_index_children(node)

    @abc.abstractmethod
    def _re_index_children(self, node: _TimelineEventNode):
        pass


class _DayIndex(_Index):
    def __init__(self, day: int):
        _Index.__init__(self, day)

    def __str__(self):
        return f"d{self.value}"

    def get_first(self):
        return self.offset

    def _re_index_children(self, node: _TimelineEventNode):
        pass


class _MonthIndex(_Index):
    def __init__(self, year: int, month: int):
        _Index.__init__(self, month)
        self._days: list[Union[_DayIndex, None]] = [None] * _get_month_count_of_days(year, month)

    def __str__(self):
        return f"m{self.value}"

    def get_first(self, day=None):
        if isinstance(day, int):
            days = len(self._days)
            idx = day - 1
            day_index = None
            while day_index is None and idx < days:
                day_index = self._days[idx]
                idx += 1

            return day_index.get_first() if isinstance(day_index, _DayIndex) else None

        return self.offset

    def _re_index_children(self, node: _TimelineEventNode):
        day: int = node.date.day
        idx: int = day - 1

        if not isinstance(self._days[idx], _DayIndex):
            self._days[idx] = _DayIndex(day)

        self._days[idx].re_index(node)


class _YearIndex(_Index):
    def __init__(self, year: int):
        _Index.__init__(self, year)
        self._months: list[Union[_MonthIndex, None]] = [None] * 12

    def __str__(self):
        return f"y{self.value}"

    def get_first(self, month=None, day=None):
        if isinstance(month, int):
            months = len(self._months)
            idx = month - 1
            month_index = None
            while month_index is None and idx < months:
                month_index = self._months[idx]
                idx += 1

            return month_index.get_first(day) if isinstance(month_index, _MonthIndex) else None

        return self.offset

    def _re_index_children(self, node: _TimelineEventNode):
        month: int = node.date.month
        idx: int = month - 1

        if not isinstance(self._months[idx], _MonthIndex):
            self._months[idx] = _MonthIndex(self.value, month)

        self._months[idx].re_index(node)


def _get_month_count_of_days(year, month) -> int:
    return monthrange(year, month)[1]
