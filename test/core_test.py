import unittest

from mabooia import option, Some, Nothing, lazy, try_of, Success, Failure


class OptionTest(unittest.TestCase):

    def test_nothing_is_empty(self):
        self.assertTrue(Nothing().is_empty())

    def test_some_is_not_empty(self):
        self.assertFalse(Some("").is_empty())

    def test_option_of_none_is_nothing(self):
        self.assertIs(option(None), Nothing())

    def test_option_of_something_is_some(self):
        self.assertEqual(option(""), Some(""))

    def test_filter_of_some(self):
        # given
        opt = Some("value")

        # then
        self.assertEqual(opt.filter(lambda v: True), Some("value"))
        self.assertEqual(opt.filter(lambda v: False), Nothing())

    def test_filter_of_nothing(self):
        # given
        opt = Nothing()

        # then
        self.assertIs(opt.filter(lambda v: True), Nothing())
        self.assertIs(opt.filter(lambda v: False), Nothing())

    def test_flatmap_of_some(self):
        # given
        opt = Some("value")

        # when
        res = opt.flatmap(lambda v: Some(v))

        # then
        self.assertEqual(res, Some("value"))

    def test_flatmap_of_nothing(self):
        # given
        opt = Nothing()

        # when
        res = opt.flatmap(lambda v: Some(v))

        # then
        self.assertEqual(res, Nothing())

    def test_if_present_of_nothing(self):
        # given
        def f(_):
            f.called = True

        f.called = False

        opt = Nothing()

        # when
        opt.if_present(f)

        # then
        self.assertFalse(f.called)

    def test_if_present_of_some(self):
        # given
        def f(arg):
            f.called = True
            f.passed = arg

        f.called = False
        f.passed = 0

        opt = Some(1)

        # when
        opt.if_present(f)

        # then
        self.assertTrue(f.called)
        self.assertEqual(opt.value, f.passed)

    def test_map_of_some(self):
        # given
        opt = Some([1, 2, 3])

        # when
        res = opt.map(lambda v: len(v))

        # then
        self.assertEqual(res, Some(3))

    def test_map_of_nothing(self):
        # given
        opt = Nothing()

        # when
        res = opt.map(lambda v: len(v))

        # then
        self.assertEqual(res, Nothing())

    def test_unzip_nothing(self):
        # given
        opt = Nothing()

        # then
        self.assertEqual(opt.unzip(lambda v: v), (Nothing(), Nothing()))

    def test_unzip_some(self):
        # given
        opt = Some((1, 2))

        # then
        self.assertEqual(opt.unzip(lambda v: v), (Some(1), Some(2)))

    def test_zip_both_nothing(self):
        # given
        opt1 = Nothing()
        opt2 = Nothing()

        # when
        res = opt1.zip(opt2)

        # then
        self.assertEqual(res, Nothing())

    def test_zip_first_nothing(self):
        # given
        opt1 = Nothing()
        opt2 = Some(2)

        # when
        res = opt1.zip(opt2)

        # then
        self.assertEqual(res, Nothing())

    def test_zip_second_nothing(self):
        # given
        opt1 = Some(1)
        opt2 = Nothing()

        # when
        res = opt1.zip(opt2)

        # then
        self.assertEqual(res, Nothing())

    def test_zip_both_some(self):
        # given
        opt1 = Some(1)
        opt2 = Some(2)

        # when
        res = opt1.zip(opt2)

        # then
        self.assertEqual(res, Some((1, 2)))


class LazyTest(unittest.TestCase):

    @staticmethod
    def _slow_function():
        return "value"

    def test_not_computed_lazy(self):
        # given
        lz = lazy(self._slow_function)

        # then
        self.assertFalse(lz.is_computed())
        self.assertEqual(lz.get_if_computed(), Nothing())

    def test_computed_lazy(self):
        # given
        lz = lazy(self._slow_function)

        # when
        value = lz.get()

        # then
        self.assertTrue(lz.is_computed())
        self.assertEqual(value, "value")
        self.assertEqual(lz.get_if_computed(), Some(value))

    def test_evaluated_lazy(self):
        # given
        lz = lazy("value")

        # then
        self.assertTrue(lz.is_computed())
        self.assertEqual(lz.get_if_computed(), Some("value"))
        self.assertEqual(lz.get(), "value")


class TryTest(unittest.TestCase):

    def test_failure(self):
        self.assertTrue(Failure("").is_failure())
        self.assertFalse(Failure("").is_success())

    def test_success(self):
        self.assertFalse(Success("").is_failure())
        self.assertTrue(Success("").is_success())

    def test_get_option(self):
        self.assertEqual(Failure(1).get_option(), Nothing())
        self.assertEqual(Success(1).get_option(), Some(1))

    def test_failure_tuple(self):
        self.assertEqual(try_of((None, "error")), Failure("error"))
        self.assertEqual(try_of((1, "error")), Failure("error"))

    def test_success_tuple(self):
        self.assertEqual(try_of((None, None)), Success(None))
        self.assertEqual(try_of((1, None)), Success(1))

    def test_failure_with_function(self):
        # given
        err = Exception()

        def fails():
            raise err

        # when
        tr = try_of(fails)

        # then
        self.assertEqual(tr, Failure(err))

    def test_success_with_function(self):
        # given
        res = object()

        def succeed():
            return res

        # when
        tr = try_of(succeed)

        # then
        self.assertEqual(tr, Success(res))

    def test_if_success_with_failure(self):
        # given
        tr = Failure("error")

        def f(arg):
            f.called = True
            f.passed = arg
            return arg + 1

        f.called = False
        f.passed = None

        # when
        res = tr.if_success(f)

        # then
        self.assertFalse(f.called)
        self.assertEqual(res, tr)

    def test_if_success_with_success(self):
        # given
        tr = Success(1)

        def f(arg):
            f.called = True
            f.passed = arg
            return arg + 1

        f.called = False
        f.passed = None

        # when
        res = tr.if_success(f)

        # then
        self.assertTrue(f.called)
        self.assertEqual(res, Success(2))
        self.assertEqual(f.passed, 1)

    def test_if_success_with_success_and_failing_func(self):
        # given
        err = Exception()
        tr = Success(1)

        def f(_):
            raise err

        # when
        res = tr.if_success(f)

        # then
        self.assertEqual(res, Failure(err))


if __name__ == '__main__':
    unittest.main()
