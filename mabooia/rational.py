import math
import re
from typing import Final

from mabooia import get_decimal_separator, get_negative_sign, get_thousand_separator, Some, lazy
from mabooia.collections.streams import EmptyStream
from mabooia.collections.mutable import LinkedList


class Rational:

    @staticmethod
    def one():
        return rat(1)

    @staticmethod
    def minus_one():
        return rat(-1)

    @staticmethod
    def zero():
        return rat(0)

    def __init__(self, num: int, den: int = 1, _simplified: bool = False):
        assert den != 0
        self._is_negative: Final[bool] = (num > 0 > den) or (num < 0 < den)
        num = abs(num)
        den = abs(den)
        self._num: Final[int] = num if not self._is_negative else -num
        self._den: Final[int] = den
        self._simplified: bool = _simplified or num == 0 or den == 1

    def __int__(self) -> int:
        s = self.simplify()
        if s.is_integer:
            return s.num
        else:
            return int(s.num / s.den)

    def __float__(self) -> float:
        s = self.simplify()
        if s.is_integer:
            return float(s.num)
        else:
            return s.num / s.den

    def __format__(self, format_spec):
        return format(float(self), format_spec)

    def __cmp__(self, other) -> int:
        return self._cmp(other)

    def __eq__(self, other) -> bool:
        return self._cmp(other) == 0

    def __ne__(self, other) -> bool:
        return self._cmp(other) != 0

    def __gt__(self, other) -> bool:
        return self._cmp(other) > 0

    def __ge__(self, other) -> bool:
        return self._cmp(other) >= 0

    def __lt__(self, other) -> bool:
        return self._cmp(other) < 0

    def __le__(self, other) -> bool:
        return self._cmp(other) <= 0

    def __neg__(self):
        return Rational(-self.num, self.den)

    def __abs__(self):
        return self if not self.is_negative else -self

    def __add__(self, other):
        o = rat(other)
        return Rational(self.num * o.den + o.num * self.den, self.den * o.den)

    def __sub__(self, other):
        o = rat(other)
        return Rational(self.num * o.den - o.num * self.den, self.den * o.den)

    def __mul__(self, other):
        o = rat(other)
        return Rational(self.num * o.num, self.den * o.den)

    def __pow__(self, power, modulo=None):
        if power == 0:
            return Rational.one()
        elif power == 1 or self == 0 or self == 1:
            return self
        elif power == -1:
            return self.invert()
        else:
            n = self.den if power < 0 else self.num
            d = self.num if power < 0 else self.den

            p = abs(power)

            n = n**p
            d = d**p

            return rat(n) / rat(d)

    def __truediv__(self, other):
        o = rat(other)
        return Rational(self.num * o.den, self.den * o.num)

    def __mod__(self, other):
        o = rat(other)
        return Rational(self.num * o.den % (self.den * o.num), self.den * o.den)

    def __floordiv__(self, other):
        o = rat(other)
        return rat((self.num * o.den) // (self.den * o.num))

    def __divmod__(self, other):
        o = rat(other)
        return self // o, self % o

    def __str__(self):
        if self._simplified and self.is_integer:
            return str(self.num)
        else:
            return f"rat({self.num}, {self.den}) = {float_rep(self, 100)}"

    def __copy__(self):
        return Rational(self.num, self.den, self._simplified)

    @property
    def num(self):
        return self._num

    @property
    def den(self):
        return self._den

    @property
    def is_negative(self):
        return self._is_negative

    @property
    def is_integer(self):
        return self.den == 1 or self.simplify().den == 1

    def simplify(self):
        if self._simplified:
            return self

        gdc = math.gcd(self.num, self.den)
        if gdc == 1:
            return self

        s_num = int(self.num / gdc)
        s_den = int(self.den / gdc)

        if s_num == s_den:
            return Rational.one()
        elif s_num == -s_den:
            return Rational.minus_one()
        else:
            return Rational(s_num, s_den, True)

    def invert(self):
        return Rational(self.den, self.num)

    # Private methods

    @staticmethod
    def _from_int(n: int):
        return Rational(n)

    @staticmethod
    def _from_float(n: float):
        return Rational._from_str(str(n))

    @staticmethod
    def _from_str(s: str):
        negative_sign = get_negative_sign()
        decimal_separator = get_decimal_separator()
        thousands_separator = get_thousand_separator()

        sign = s.startswith(negative_sign)

        split = s.split(decimal_separator)
        integer_part = split[0].replace(thousands_separator, '')
        fractional_part = split[1] if len(split) > 1 else ''

        r1 = Rational(int(integer_part))
        r2 = Rational(int(fractional_part) * (-1 if sign else 1), 10 ** len(fractional_part))\
            if fractional_part != ''\
            else 0

        return (r1 + r2).simplify()

    @staticmethod
    def _from_rat_rep(m: re.Match):
        thou_sep = get_thousand_separator()
        num = m.group('num').replace(' ', '').replace(thou_sep, '')
        den = m.group('den').replace(' ', '').replace(thou_sep, '')

        return Rational(int(num), int(den))

    @staticmethod
    def _from_float_rep(fr):
        ip = fr.int_part
        dp = fr.decimal_part
        rd = fr.repeated_decimal
        sign = ip.startswith(get_negative_sign())

        len_dp = len(dp)
        len_rd = len(rd)

        ip_rat = rat(ip)
        dec_sep = get_decimal_separator()
        dp_rat = rat(f"0{dec_sep}{dp}")
        rd_rat = rat(rd) / (rat(10) ** (len_dp + len_rd) - rat(10) ** len_dp)

        return (ip_rat + dp_rat + rd_rat) * (-1 if sign else 1)

    @staticmethod
    def of(obj):
        if isinstance(obj, Rational):
            return obj
        elif isinstance(obj, int):
            return Rational(obj)
        elif isinstance(obj, float):
            return Rational._from_float(obj)
        elif isinstance(obj, str):
            m = match_rational_rep_format(obj)
            if m:
                return Rational._from_rat_rep(m)
            else:
                m = match_float_rep_format(obj)
                if m:
                    return Rational._from_float_rep(match_to_float_rep(m))
                else:
                    return Rational._from_str(obj)
        else:
            raise TypeError

    def _cmp(self, other):
        o = rat(other)
        res = self.num * o.den - o.num * self.den
        if res > 0:
            return 1
        elif res < 0:
            return -1
        else:
            return 0


class FloatRepresentation:
    def __init__(self, int_part: str, decimal_part: str, repeated_decimal: str):
        self._int_part = int_part
        self._decimal_part = decimal_part
        self._repeated_decimal = repeated_decimal

    def __str__(self):
        decimal_separator = get_decimal_separator()

        period_chars = f"({self.repeated_decimal})"\
            if self.repeated_decimal != ''\
            else ''

        return f"{self.int_part}{decimal_separator}{self.decimal_part}{period_chars}"

    @property
    def int_part(self):
        return self._int_part

    @property
    def decimal_part(self):
        return self._decimal_part

    @property
    def repeated_decimal(self):
        return self._repeated_decimal


def rat(obj) -> Rational:
    return Rational.of(obj)


def __get_float_rep_regex():
    neg_sign = get_negative_sign()
    thou_sep = get_thousand_separator()
    dec_sep = get_decimal_separator()
    return re.compile(f"^(?P<ip>{neg_sign}?\\s*[\\d{thou_sep}\\s]+)\\s*"
                      f"{dec_sep}\\s*(?P<dp>\\d+)?\\s*\\(\\s*(?P<rp>[\\d\\s]+)\\s*\\)$")


__float_rep_regex_lazy = lazy(__get_float_rep_regex)


def __get_rational_rep_format():
    neg_sign = get_negative_sign()
    thou_sep = get_thousand_separator().replace('.', '\\.')
    div_sep = '/'
    return re.compile(f"^(?P<num>{neg_sign}?\\s*[\\d{thou_sep}\\s]+)\\s*"
                      f"{div_sep}\\s*(?P<den>{neg_sign}?\\s*[\\d+{thou_sep}\\s]+)?\\s*$")


__get_rational_rep_format_lazy = lazy(__get_rational_rep_format)


def match_float_rep_format(text: str) -> re.Match:
    return __float_rep_regex_lazy.get().match(text)


def match_rational_rep_format(text: str) -> re.Match:
    return __get_rational_rep_format_lazy.get().match(text)


def match_to_float_rep(m: re.Match) -> FloatRepresentation:
    thou_sep = get_thousand_separator()
    ip_str = m.group('ip')
    dp_str = m.group('dp')
    rp_str = m.group('rp')
    ip = ip_str.replace(' ', '').replace(thou_sep, '') if ip_str is not None else 0
    dp = dp_str.replace(' ', '') if dp_str is not None else ''
    rp = rp_str.replace(' ', '') if rp_str is not None else ''

    return FloatRepresentation(ip, dp, rp)


def float_rep(obj, max_decimals: int = 100):

    def _from_rat(_r):
        def _float_rep(continue_cond):
            num = abs(_r.num)
            den = abs(_r.den)

            int_part = str(num // den)
            decimal_part = EmptyStream()
            repeated_part = ''
            remaining = EmptyStream()

            rem = num % den
            while rem != 0 and continue_cond(int_part, decimal_part, repeated_part):
                cur_quot = LinkedList()
                remaining = remaining.prepend(rem)
                num = rem * 10
                while num < den:
                    num *= 10
                    cur_quot.append('0')

                quot = num // den
                cur_quot.append(str(quot))
                rem = num % den
                decimal_part = decimal_part.prepend(''.join(cur_quot))

                idx = remaining.index_of(rem)
                if idx >= 0:
                    repeated_part = ''.join(reversed(decimal_part.take(idx + 1).to_list()))
                    decimal_part = decimal_part.skip(idx + 1)
                    decimal_part_head = decimal_part.head_option
                    if isinstance(decimal_part_head, Some) and decimal_part_head.value.endswith(repeated_part):
                        d_str = decimal_part_head.value
                        decimal_part = decimal_part.skip(1).prepend(d_str.value[:len(d_str) - len(repeated_part)])
                    break

            if int_part == '0' and _r.is_negative:
                int_part = f"-{int_part}"

            decimal_part_str = ''.join(reversed(decimal_part.to_list()))

            return FloatRepresentation(
                int_part,
                decimal_part_str,
                repeated_part
            )

        return _float_rep(lambda _ip, _dp, _rp: len(_dp) + len(_rp) <= max_decimals)

    if isinstance(obj, Rational):
        return _from_rat(obj)
    else:
        m = match_float_rep_format(str(obj))
        if isinstance(obj, str) and m:
            return match_to_float_rep(m)
        else:
            r = rat(obj)
            return _from_rat(r)
