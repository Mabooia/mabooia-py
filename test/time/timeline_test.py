import unittest
from datetime import date

from mabooia.collections import Stream
from mabooia.time import Timeline, TimelineEvent, in_date, in_range


class TimelineTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        events = cls._events = [
            TimelineEvent(date(2020, 1, 6), "ev-1113"),
            TimelineEvent(date(2020, 12, 31), "ev-1116"),
            TimelineEvent(date(2020, 1, 1), "ev-1112"),
            TimelineEvent(date(2020, 3, 12), "ev-1114"),
            TimelineEvent(date(2019, 10, 18), "ev-1111"),
            TimelineEvent(date(2021, 3, 12), "ev-1117"),
            TimelineEvent(date(2020, 7, 25), "ev-1115"),
            TimelineEvent(date(2021, 8, 3), "ev-1118"),
        ]
        cls._sorted_events = sorted(events, key=lambda e: e.date)
        tl = cls._timeline = Timeline()
        for ev in events:
            tl.add_event(ev)

    def test_get_all_events(self):
        # given
        tl: Timeline = self._timeline
        expected = self._sorted_events

        # when
        res = tl.events()

        # then
        self.assertEqual(expected, res.to_list())

    def test_get_all_events_of_2020(self):
        # given
        tl: Timeline = self._timeline
        expected = Stream\
            .of(self._sorted_events)\
            .filter(lambda ev: ev.date.year == 2020)\
            .to_list()

        # when
        res = tl.events(in_date(2020))

        # then
        self.assertTrue(res.is_not_empty)
        self.assertEqual(expected, res.to_list())

    def test_get_all_events_of_2020_Jan(self):
        # given
        tl: Timeline = self._timeline
        expected = Stream\
            .of(self._sorted_events)\
            .filter(lambda ev: ev.date.year == 2020 and ev.date.month == 1)\
            .to_list()

        # when
        res = tl.events(in_date(2020, 1))

        # then
        self.assertTrue(res.is_not_empty)
        self.assertEqual(expected, res.to_list())

    def test_get_all_events_of_2020_Jan_6(self):
        # given
        tl: Timeline = self._timeline
        expected = Stream\
            .of(self._sorted_events)\
            .filter(lambda ev: ev.date.year == 2020 and ev.date.month == 1 and ev.date.day == 6)\
            .to_list()

        # when
        res = tl.events(in_date(2020, 1, 6))

        # then
        self.assertTrue(res.is_not_empty)
        self.assertEqual(expected, res.to_list())

    def test_get_all_events_of_2020_Sep(self):
        # given
        tl: Timeline = self._timeline

        # when
        res = tl.events(in_date(2020, 9))

        # then
        self.assertTrue(res.is_empty)

    def test_get_all_events_from_2020_Dec_to_2021_Jul(self):
        # given
        tl: Timeline = self._timeline

        def is_in_range(dt: date) -> bool:
            return date(2020, 12, 1) <= dt <= date(2021, 7, 31)

        expected = Stream\
            .of(self._sorted_events)\
            .filter(lambda ev: is_in_range(ev.date))\
            .to_list()

        # when
        res = tl.events(in_range(from_year=2020, from_month=12, to_year=2021, to_month=7))

        # then
        self.assertTrue(res.is_not_empty)
        self.assertEqual(expected, res.to_list())


if __name__ == '__main__':
    unittest.main()
