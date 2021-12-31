import math
import unittest

from mabooia import Nothing, Some
from mabooia.collections import Stream, EmptyStream


class StreamTest(unittest.TestCase):

    def test_iter(self):
        for _ in EmptyStream():
            self.fail("Never should reach this line")

        ls = [1, 2, 3]
        res = []
        for it in Stream.of(ls):
            res.append(it)

        self.assertEqual(ls, res)

    def test_len(self):
        self.assertEqual(0, len(EmptyStream()))
        self.assertEqual(5, len(Stream.of([1, 2, 3, 4, 5])))

    def test_str(self):
        self.assertEqual("Stream[]", str(EmptyStream()))
        self.assertEqual("Stream[1, 2, 3, 4, 5]", str(Stream.of([1, 2, 3, 4, 5])))

    def test_is_empty(self):
        self.assertTrue(EmptyStream().is_empty)
        self.assertFalse(Stream.of([1]).is_empty)
        self.assertFalse(Stream.of([1, 2, 3, 4, 5]).is_empty)

    def test_is_not_empty(self):
        self.assertFalse(EmptyStream().is_not_empty)
        self.assertTrue(Stream.of([1]).is_not_empty)
        self.assertTrue(Stream.of([1, 2, 3, 4, 5]).is_not_empty)

    def test_head_option(self):
        self.assertEqual(Nothing(), EmptyStream().head_option)
        self.assertEqual(Some(1), Stream.of([1, 2, 3, 4, 5]).head_option)

    def test_tail(self):
        self.assertEqual(EmptyStream(), EmptyStream().tail)
        self.assertTrue(Stream.of([1, 2, 3, 4, 5]).tail.corresponds([2, 3, 4, 5]))
        self.assertTrue(Stream.of([2, 3, 4, 5]).tail.corresponds([3, 4, 5]))
        self.assertTrue(Stream.of([3, 4, 5]).tail.corresponds([4, 5]))
        self.assertTrue(Stream.of([4, 5]).tail.corresponds([5]))
        self.assertEqual(Stream.of([5]).tail, EmptyStream())

    def test_all(self):
        self.assertTrue(EmptyStream().all(lambda _: False))
        self.assertTrue(Stream.of([1, 2, 3, 4, 5]).all(lambda it: it < 10))
        self.assertFalse(Stream.of([1, 2, 3, 4, 5]).all(lambda it: it < 5))
        self.assertFalse(Stream.of([1, 2, 3, 4, 5]).all(lambda it: it < 1))

    def test_append(self):
        # given
        test_cases = [
            EmptyStream(),
            Stream.of([1, 2, 3, 4, 5]),
            Stream.of([1, 2, 3, 4]),
            Stream.of([1, 2, 3]),
            Stream.of([1, 2]),
            Stream.of([1]),
        ]

        for stream in test_cases:
            # when
            res = stream.append("any")

            # then
            self.assertTrue(res.is_not_empty)
            self.assertEqual(len(stream) + 1, len(res))
            self.assertEqual(Some("any"), res.rear_option)

    def test_append_stream(self):
        self.assertEqual(
            EmptyStream(),
            EmptyStream().append_stream(EmptyStream())
        )
        self.assertTrue(
            EmptyStream()
            .append_stream(Stream.of([1, 2, 3]))
            .corresponds([1, 2, 3])
        )
        self.assertTrue(
            Stream.of([1, 2, 3])
            .append_stream(EmptyStream())
            .corresponds([1, 2, 3])
        )
        self.assertTrue(
            Stream.of([1, 2, 3])
            .append_stream(Stream.of([4, 5, 6]))
            .corresponds([1, 2, 3, 4, 5, 6])
        )

    def test_correspond(self):
        # given
        test_cases = [
            [1, 2, 3, 4, 5],
            [1, 2, 3, 4],
            [1, 2, 3],
            [1, 2],
            [1],
            [],
        ]

        for ls in test_cases:
            # given
            stream = Stream.of(ls)

            # then
            self.assertTrue(stream.corresponds(ls))

    def test_exists(self):
        self.assertFalse(EmptyStream().exists(lambda _: True))
        self.assertTrue(Stream.of([1, 2, 3, 4, 5]).exists(lambda it: it < 10))
        self.assertTrue(Stream.of([1, 2, 3, 4, 5]).exists(lambda it: it < 3))
        self.assertFalse(Stream.of([1, 2, 3, 4, 5]).exists(lambda it: it < 1))

    def test_filter(self):
        self.assertEqual(EmptyStream(), EmptyStream().filter(lambda _: True))
        self.assertTrue(Stream.of([1, 2, 3, 4, 5]).filter(lambda it: it % 2 == 0).corresponds([2, 4]))
        self.assertTrue(Stream.of([1, 2, 3, 4, 5]).filter(lambda it: it % 2 != 0).corresponds([1, 3, 5]))
        self.assertTrue(Stream.of([1, 2, 3, 4, 5]).filter(lambda _: True).corresponds([1, 2, 3, 4, 5]))
        self.assertTrue(Stream.of([1, 2, 3, 4, 5]).filter(lambda _: False).is_empty)

    def test_flatmap(self):
        self.assertEqual(EmptyStream(), EmptyStream().flatmap(lambda it: Some(it)))
        self.assertEqual(
            EmptyStream(),
            EmptyStream().flatmap(lambda it: Stream.of([1 * it, 2 * it, 3 * it]))
        )

        self.assertTrue(
            Stream.of([1, 2, 3])
            .flatmap(lambda it: Some(it) if it % 2 != 0 else Nothing())
            .corresponds([1, 3])
        )

        self.assertTrue(
            Stream.of([1, 2, 3])
            .flatmap(lambda it: Stream.of([1 * it, 2 * it, 3 * it]) if it % 2 != 0 else Nothing())
            .corresponds([1, 2, 3, 3, 6, 9])
        )

    def test_flatten(self):
        self.assertEqual(EmptyStream(), EmptyStream().flatten())

        self.assertTrue(
            Stream.of([1, 2, 3])
            .map(lambda it: Some(it) if it % 2 != 0 else Nothing())
            .flatten()
            .corresponds([1, 3])
        )

        self.assertTrue(
            Stream.of([1, 2, 3])
            .map(lambda it: Stream.of([1 * it, 2 * it, 3 * it]) if it % 2 != 0 else Nothing())
            .flatten()
            .corresponds([1, 2, 3, 3, 6, 9])
        )

    def test_fold(self):
        # given
        def add(acc, it):
            return acc + it

        # then
        self.assertEqual(15, Stream.of([1, 2, 3, 4, 5]).fold(0, add))
        self.assertEqual(10, Stream.of([1, 2, 3, 4]).fold(0, add))
        self.assertEqual(6, Stream.of([1, 2, 3]).fold(0, add))
        self.assertEqual(3, Stream.of([1, 2]).fold(0, add))
        self.assertEqual(1, Stream.of([1]).fold(0, add))
        self.assertEqual(0, EmptyStream().fold(0, add))

    def test_map(self):
        self.assertEqual(
            EmptyStream(),
            EmptyStream().map(lambda it: it * 3)
        )
        self.assertTrue(
            Stream.of([1, 2, 3])
            .map(lambda it: it * 3)
            .corresponds([3, 6, 9])
        )

    def test_map_indexed(self):
        self.assertEqual(
            EmptyStream(),
            EmptyStream().map_indexed(lambda n, idx: n * 3)
        )
        self.assertTrue(
            Stream.of([1, 2, 3])
            .map_indexed(lambda n, idx: f"{idx}: {n * 3}")
            .corresponds(["0: 3", "1: 6", "3: 9"])
        )

    def test_prepend(self):
        # given
        test_cases = [
            EmptyStream(),
            Stream.of([1, 2, 3, 4, 5]),
            Stream.of([1, 2, 3, 4]),
            Stream.of([1, 2, 3]),
            Stream.of([1, 2]),
            Stream.of([1]),
        ]

        for stream in test_cases:
            # when
            res = stream.prepend("any")

            # then
            self.assertTrue(res.is_not_empty)
            self.assertEqual(len(stream) + 1, len(res))
            self.assertEqual(Some("any"), res.head_option)

    def test_prepend_stream(self):
        self.assertEqual(
            EmptyStream(),
            EmptyStream().prepend_stream(EmptyStream())
        )
        self.assertTrue(
            EmptyStream()
            .prepend_stream(Stream.of([1, 2, 3]))
            .corresponds([1, 2, 3])
        )
        self.assertTrue(
            Stream.of([1, 2, 3])
            .prepend_stream(EmptyStream())
            .corresponds([1, 2, 3])
        )
        self.assertTrue(
            Stream.of([1, 2, 3])
            .prepend_stream(Stream.of([4, 5, 6]))
            .corresponds([4, 5, 6, 1, 2, 3])
        )

    def test_skip(self):
        self.assertEqual(
            EmptyStream(),
            EmptyStream().skip(3)
        )
        self.assertEqual(
            EmptyStream(),
            Stream.of([1, 2, 3, 4, 5]).skip(5)
        )
        self.assertEqual(
            EmptyStream(),
            Stream.of([1, 2, 3, 4, 5]).skip(10)
        )
        self.assertTrue(
            Stream.of([1, 2, 3, 4, 5])
            .skip(3)
            .corresponds([4, 5])
        )

    def test_skip_while(self):
        self.assertEqual(
            EmptyStream(),
            EmptyStream().skip_while(lambda _: False)
        )
        self.assertEqual(
            EmptyStream(),
            Stream.of([1, 2, 3, 4, 5]).skip_while(lambda _: True)
        )
        self.assertEqual(
            EmptyStream(),
            Stream.of([1, 2, 3, 4, 5]).skip_while(lambda n: n < 10)
        )
        self.assertTrue(
            Stream.of([1, 2, 3, 4, 5])
            .skip_while(lambda n: n < 4)
            .corresponds([4, 5])
        )
        self.assertTrue(
            Stream.of([1, 2, 3, 4, 5])
            .skip_while(lambda n: False)
            .corresponds([1, 2, 3, 4, 5])
        )

    def test_skip_while_indexed(self):
        self.assertEqual(
            EmptyStream(),
            EmptyStream().skip_while_indexed(lambda n, idx: False)
        )
        self.assertEqual(
            EmptyStream(),
            Stream.of([1, 2, 3, 4, 5]).skip_while_indexed(lambda n, idx: True)
        )
        self.assertEqual(
            EmptyStream(),
            Stream.of([1, 2, 3, 4, 5]).skip_while_indexed(lambda n, idx: n < 10 or idx < 8)
        )
        self.assertTrue(
            Stream.of([1, 2, 3, 4, 5])
            .skip_while_indexed(lambda n, idx: n < 7 and idx < 3)
            .corresponds([4, 5])
        )
        self.assertTrue(
            Stream.of([1, 2, 3, 4, 5])
            .skip_while_indexed(lambda n, idx: False)
            .corresponds([1, 2, 3, 4, 5])
        )

    def test_take(self):
        self.assertEqual(
            EmptyStream(),
            EmptyStream().take(3)
        )
        self.assertTrue(
            Stream.of([1, 2, 3, 4, 5])
            .take(5)
            .corresponds([1, 2, 3, 4, 5])
        )
        self.assertTrue(
            Stream.of([1, 2, 3, 4, 5])
            .take(10)
            .corresponds([1, 2, 3, 4, 5])
        )
        self.assertTrue(
            Stream.of([1, 2, 3, 4, 5])
            .take(3)
            .corresponds([1, 2, 3])
        )

    def test_take_while(self):
        self.assertEqual(
            EmptyStream(),
            EmptyStream().take_while(lambda _: True)
        )
        self.assertTrue(
            Stream.of([1, 2, 3, 4, 5])
            .take_while(lambda _: True)
            .corresponds([1, 2, 3, 4, 5])
        )
        self.assertTrue(
            Stream.of([1, 2, 3, 4, 5])
            .take_while(lambda n: n < 10)
            .corresponds([1, 2, 3, 4, 5])
        )
        self.assertTrue(
            Stream.of([1, 2, 3, 4, 5])
            .take_while(lambda n: n < 4)
            .corresponds([1, 2, 3])
        )
        self.assertEqual(
            EmptyStream(),
            Stream.of([1, 2, 3, 4, 5])
            .take_while(lambda n: False)
        )

    def test_take_while_indexed(self):
        self.assertEqual(
            EmptyStream(),
            EmptyStream().take_while_indexed(lambda n, idx: True)
        )
        self.assertEqual(
            EmptyStream(),
            Stream.of([1, 2, 3, 4, 5]).take_while_indexed(lambda n, idx: False)
        )
        self.assertTrue(
            Stream.of([1, 2, 3, 4, 5])
            .take_while_indexed(lambda n, idx: idx < 3)
            .corresponds([1, 2, 3])
        )
        self.assertEqual(
            EmptyStream(),
            Stream.of([1, 2, 3, 4, 5]).take_while_indexed(lambda n, idx: False)
        )

    def test_unzip(self):
        self.assertEqual(
            (EmptyStream(), EmptyStream()),
            EmptyStream().unzip(lambda _: (1, 2))
        )

        # when
        s1, s2 = Stream.of([1, 4, 9, 16, 25]).unzip(lambda n: (math.sqrt(n), -math.sqrt(n)))

        # then
        self.assertTrue(s1.corresponds([1, 2, 3, 4, 5]))
        self.assertTrue(s2.corresponds([-1, -2, -3, -4, -5]))

    def test_zip(self):
        self.assertEqual(
            EmptyStream(),
            EmptyStream().zip(EmptyStream())
        )
        self.assertEqual(
            EmptyStream(),
            EmptyStream().zip(Stream.of([1, 2, 3]))
        )
        self.assertEqual(
            EmptyStream(),
            Stream.of([1, 2, 3]).zip(EmptyStream())
        )

        self.assertTrue(
            Stream.of([1, 2, 3])
            .zip(Stream.of(["a", "b", "c"]))
            .corresponds([(1, "a"), (2, "b"), (3, "c")])
        )
        self.assertTrue(
            Stream.of([1, 2, 3, 4])
            .zip(Stream.of(["a", "b", "c"]))
            .corresponds([(1, "a"), (2, "b"), (3, "c")])
        )
        self.assertTrue(
            Stream.of([1, 2, 3])
            .zip(Stream.of(["a", "b", "c", "d"]))
            .corresponds([(1, "a"), (2, "b"), (3, "c")])
        )


if __name__ == "__main__":
    unittest.main()
