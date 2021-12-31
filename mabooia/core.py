import abc
import threading
from typing import *


class Singleton(object):
    def __new__(cls, *args, **keywords):
        instance = cls.__dict__.get("__it__")
        if instance is not None:
            return instance

        cls.__it__ = instance = object.__new__(cls)
        instance.init(*args, **keywords)
        return instance

    def init(self, *args, **keywords):
        pass


# Option

class Option(abc.ABC):

    def is_empty(self):
        return not self.is_not_empty()

    def is_not_empty(self):
        return isinstance(self, Some)

    def get_or_else(self, default):
        if isinstance(self, Some):
            return self.value

        return default() if isinstance(default, Callable) else default

    def or_else(self, default_opt):
        if isinstance(self, Some):
            return self

        return default_opt() if isinstance(default_opt, Callable) else default_opt

    def filter(self, f: Callable, is_true: bool = True):
        return Some(self.value) if isinstance(self, Some) and f(self.value) == is_true else Nothing()

    def flatmap(self, mapper: Callable):
        if isinstance(self, Some):
            opt = mapper(self.value)

            assert isinstance(opt, Option)
            return Some(opt.value) if isinstance(opt, Some) else Nothing()

        return Nothing()

    def if_present(self, f: Callable):
        if isinstance(self, Some):
            f(self.value)

    def map(self, mapper: Callable):
        return Some(mapper(self.value)) if isinstance(self, Some) else Nothing()

    def unzip(self, f: Callable) -> tuple:
        if isinstance(self, Some):
            t: tuple = f(self.value)
            if isinstance(t, tuple):
                return Some(t[0]), Some(t[1])

        return Nothing(), Nothing()

    def zip(self, other):
        if isinstance(self, Some) and isinstance(other, Some):
            return Some((self.value, other.value))

        return Nothing()


class Some(Option):
    def __init__(self, value):
        self.value: Final = value

    def __eq__(self, other: Option):
        return isinstance(other, Some) and self.value == other.value

    def __str__(self):
        return f"Some({self.value})"


class Nothing(Option, Singleton):
    def __str__(self):
        return "Nothing"


def option(value):
    return Some(value) if value is not None else Nothing()


# Lazy

class Lazy(abc.ABC):

    @abc.abstractmethod
    def is_computed(self) -> bool:
        pass

    @abc.abstractmethod
    def get_if_computed(self) -> Option:
        pass

    @abc.abstractmethod
    def get(self):
        pass


class EvaluatedLazy(Lazy):
    def __init__(self, value):
        self._value: Final = value

    def is_computed(self) -> bool:
        return True

    def get_if_computed(self) -> Option:
        return Some(self._value)

    def get(self):
        return self._value

    def __str__(self):
        return f"Lazy({self._value})"


class SynchronizedLazy(Lazy):
    def __init__(self, f: Callable):
        self._f = f
        self._is_computed = False
        self._value: Optional = None
        self._lock = threading.Lock()

    def is_computed(self) -> bool:
        return self._is_computed

    def get_if_computed(self) -> Option:
        return Some(self._value) if self._is_computed else Nothing()

    def get(self):
        self._compute_if_needed()
        return self._value

    def _compute_if_needed(self):
        if not self._is_computed:
            with self._lock:
                if not self._is_computed:
                    self._value = self._f()
                    self._is_computed = True

    def __str__(self):
        if self._is_computed:
            return f"Lazy({self._value})"
        else:
            return "Lazy(...)"


def lazy(arg) -> Lazy:
    if isinstance(arg, Lazy):
        return arg
    elif isinstance(arg, Callable):
        return SynchronizedLazy(arg)
    else:
        return EvaluatedLazy(arg)


# Try

class Try(abc.ABC):
    def is_success(self) -> bool:
        return isinstance(self, Success)

    def is_failure(self) -> bool:
        return isinstance(self, Failure)

    def get_option(self):
        if isinstance(self, Success):
            return Some(self.result)

        return Nothing()

    def get_tuple(self) -> tuple[Optional, Optional[Exception]]:
        if isinstance(self, Success):
            return self.result, None

        elif isinstance(self, Failure):
            return None, self.err

        else:
            return None, None

    def if_success(self, f: Callable):
        if isinstance(self, Success):
            res = self.result

            def g():
                return f(res)

            return try_of(g)

        return self

    def if_failure(self, recover_func: Callable):
        if isinstance(self, Failure):
            err = self.err

            def g():
                return recover_func(err)

            return try_of(g)

        return self

    def if_failure_with(self, err_type, recover_func: Callable):
        if isinstance(self, Failure) and isinstance(self.err, err_type):
            err = self.err

            def g():
                return recover_func(err)

            return try_of(g)

        return self

    def raise_if_failure(self):
        if isinstance(self, Failure):
            raise self.err


class Success(Try):
    def __init__(self, result):
        self.result: Final = result

    def __eq__(self, other: Try):
        if isinstance(other, Success):
            return self.result == other.result

        return False

    def __str__(self):
        return f"Success({self.result})"


class Failure(Try):
    def __init__(self, err: Exception):
        self.err: Final[Exception] = err

    def __eq__(self, other: Try):
        if isinstance(other, Failure):
            return self.err == other.err

        return False

    def __str__(self):
        return f"Failure({self.err})"


def try_of(arg) -> Try:
    if isinstance(arg, tuple):
        if arg[1] is None:
            return Success(arg[0])
        return Failure(arg[1])

    elif isinstance(arg, Callable):
        try:
            res = arg()
            return Success(res)
        except Exception as ex:
            return Failure(ex)

    else:
        return Success(arg)
