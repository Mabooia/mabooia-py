import unittest

from mabooia import rat, Rational


class RationalTest(unittest.TestCase):

    def test_rat(self):
        # given
        r1 = Rational(2, 8)

        # then
        self.assertEqual(2, r1.num)
        self.assertEqual(8, r1.den)
        self.assertFalse(r1.is_integer)
        self.assertFalse(r1.is_negative)
        self.assertEqual(0.25, r1)
        self.assertEqual(0.25, r1.simplify())
        self.assertEqual(1, r1.simplify().num)
        self.assertEqual(4, r1.simplify().den)
        self.assertEqual(Rational(1, 4), r1)

    def test_rat_from_int(self):
        # given
        r1 = rat(100)
        r2 = rat(-100)

        # then
        self.assertEqual(100, r1.num)
        self.assertEqual(1, r1.den)
        self.assertTrue(r1.is_integer)
        self.assertFalse(r1.is_negative)

        self.assertEqual(-100, r2.num)
        self.assertEqual(1, r2.den)
        self.assertTrue(r2.is_integer)
        self.assertTrue(r2.is_negative)

    def test_rat_from_float(self):
        # given
        r1 = rat(200.240000000003)
        r2 = rat(-200.240000000003)

        # then
        self.assertEqual(200240000000003, r1.num)
        self.assertEqual(1000000000000, r1.den)
        self.assertFalse(r1.is_integer)
        self.assertFalse(r1.is_negative)

        self.assertEqual(-200240000000003, r2.num)
        self.assertEqual(1000000000000, r2.den)
        self.assertFalse(r2.is_integer)
        self.assertTrue(r2.is_negative)

    def test_rat_from_str(self):
        self.assertEqual(Rational(3, 10), rat('0.3'))
        self.assertEqual(Rational(1, 3), rat('0.(3)'))
        self.assertEqual(Rational(-1, 3), rat('-0.(3)'))
        self.assertEqual(Rational(-1, 333), rat('- 1 / 333'))
        self.assertEqual(Rational(1222, 3333), rat('- 1, 222 / -3,333'))

    def test_arithmetic_operations(self):
        self.assertEqual(rat(102.73), rat(100.23) + rat(2.5))
        self.assertEqual(rat(97.73), rat(100.23) - rat(2.5))
        self.assertEqual(rat(250.575), rat(100.23) * rat(2.5))
        self.assertEqual(rat(40.092), rat(100.23) / rat(2.5))
        self.assertEqual(rat(40), rat(100.23) // rat(2.5))
        self.assertEqual(rat(0.23), rat(100.23) % rat(2.5))
        self.assertEqual(Rational(274756336065621325000000000000, 2617821370127249000000000000), rat(100.23) ** 1.01)

    def test_boolean_operations(self):
        self.assertTrue(rat('1/3') == rat('0.(3)'))
        self.assertTrue(rat('0.3333333333') != rat('0.(3)'))
        self.assertTrue(rat('0.3333333333') < rat('0.(3)') < rat('0.3333333334'))
        self.assertTrue(rat('0.3333333333') <= rat('0.(3)') <= rat('0.3333333334'))
        self.assertTrue(rat('0.(3)') <= rat('0.(3)') <= rat('0.(3)'))


if __name__ == '__main__':
    unittest.main()
