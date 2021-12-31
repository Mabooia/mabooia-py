import abc

from datetime import date

from mabooia import lazy, Rational
from mabooia.accounting import Currency
from mabooia.collections.mutable import LinkedList
from mabooia.crypto import sha256_to_str, bin_to_hex
from mabooia.finance import Security


class Event(abc.ABC):
    def __init__(self, account_id: str, transaction_date: date, settlement_date: date):
        self._account_d = account_id
        self._transaction_date = transaction_date
        self._settlement_date = settlement_date
        self._id = lazy(lambda: sha256_to_str(self._id_keys, bin_to_hex))

    @property
    def id(self) -> str:
        return self._id.get()

    @property
    def account_id(self) -> str:
        return self._account_d

    @property
    def transaction_date(self) -> date:
        return self._transaction_date

    @property
    def settlement_date(self) -> date:
        return self._settlement_date

    @property
    @abc.abstractmethod
    def currency(self) -> Currency:
        pass

    @property
    def _id_keys(self) -> LinkedList:
        return LinkedList([
            str(self.__class__),
            self.account_id,
            self.transaction_date.strftime('%Y-%m-%d'),
            self.settlement_date.strftime('%Y-%m-%d'),
            str(self.currency),
        ])


class SecurityEvent(Event, abc.ABC):
    def __init__(self, account_id: str, transaction_date: date, settlement_date: date, security: Security):
        super(SecurityEvent, self).__init__(account_id, transaction_date, settlement_date)
        self._security = security

    @property
    def security(self):
        return self._security

    @property
    def symbol(self) -> str:
        return self.security.symbol

    @property
    def currency(self) -> Currency:
        return self.security.currency

    @property
    def _id_keys(self) -> LinkedList:
        return super()._id_keys.append_iterable([self.symbol])


class Trade(SecurityEvent):
    def __init__(self, account_id: str, transaction_date: date, settlement_date: date, security: Security,
                 quantity: Rational, price: Rational, fee: Rational):
        super(Trade, self).__init__(account_id, transaction_date, settlement_date, security)
        self._quantity = quantity
        self._price = price
        self._fee = fee

    def __str__(self):
        return f"{self.trade_operation} {abs(self.quantity)} {self.symbol} at {self.price} {self.currency}"

    @property
    def is_buy(self):
        return self.quantity > 0

    @property
    def is_sell(self):
        return self.quantity < 0

    @property
    def quantity(self) -> Rational:
        return self._quantity

    @property
    def price(self) -> Rational:
        return self._price

    @property
    def fee(self) -> Rational:
        return self._fee

    @property
    def sub_total(self) -> Rational:
        return abs(self.quantity) * self.security.shares_per_unit * self.price

    @property
    def total(self) -> Rational:
        return self.sub_total + (self._fee if self.is_buy else -self._fee)

    @property
    def total_vector(self) -> Rational:
        return self.total if self.is_sell else -self.total

    @property
    def avg_price(self) -> Rational:
        return self.total / self.quantity

    @property
    def trade_operation(self) -> str:
        typ = "UNKNOWN"
        if self.is_buy:
            typ = "BUY"
        elif self.is_sell:
            typ = "SELL"

        return typ

    @property
    def _id_keys(self) -> LinkedList:
        return super(Trade, self)._id_keys.append_iterable([
            str(self.quantity),
            str(self.price),
            str(self.fee),
        ])


class Dividend(SecurityEvent):
    def __init__(self, account_id: str, transaction_date: date, settlement_date: date,
                 security: Security, amount: Rational):
        super(Dividend, self).__init__(account_id, transaction_date, settlement_date, security)
        self._amount = amount

    def __str__(self):
        return f"DIV {self.symbol} {self.amount} {self.currency}"

    @property
    def amount(self) -> Rational:
        return self._amount

    @property
    def _id_keys(self) -> LinkedList:
        return super(Dividend, self)._id_keys.append_iterable([
            str(self.amount),
        ])


class TransformFrom(SecurityEvent):
    def __init__(self, account_id: str, transaction_date: date, settlement_date: date, security: Security,
                 quantity: Rational):
        super(TransformFrom, self).__init__(account_id, transaction_date, settlement_date, security)
        self._quantity = quantity

    def __str__(self):
        return f"Transform from {self.symbol}"

    @property
    def quantity(self) -> Rational:
        return self._quantity

    def _id_keys(self) -> LinkedList:
        return super(TransformFrom, self)._id_keys.append_iterable([
            str(self.quantity),
        ])


class TransformInto(SecurityEvent):
    def __init__(self, account_id: str, transaction_date: date, settlement_date: date, security: Security,
                 quantity: Rational):
        super(TransformInto, self).__init__(account_id, transaction_date, settlement_date, security)
        self._quantity = quantity

    def __str__(self):
        return f"Transform into {self.symbol}"

    @property
    def quantity(self) -> Rational:
        return self._quantity

    def _id_keys(self) -> LinkedList:
        return super(TransformInto, self)._id_keys.append_iterable([
            str(self.quantity),
        ])


class OptionExpiration(SecurityEvent):
    def __init__(self, account_id: str, transaction_date: date, settlement_date: date, security: Security,
                 quantity: Rational):
        super(OptionExpiration, self).__init__(account_id, transaction_date, settlement_date, security)
        self._quantity = quantity

    def __str__(self):
        return f"Expired {self.quantity} of {self.symbol}"

    @property
    def quantity(self) -> Rational:
        return self._quantity

    def _id_keys(self) -> LinkedList:
        return super(OptionExpiration, self)._id_keys.append_iterable([
            str(self.quantity),
        ])


class UnknownEvent(Event):
    def __init__(self, account_id: str, transaction_date: date, settlement_date: date, info):
        super(UnknownEvent, self).__init__(account_id, transaction_date, settlement_date)
        self._info = info

    def __str__(self):
        return f"UNKNOWN ..."

    @property
    def info(self):
        return self._info

    @property
    def currency(self) -> Currency:
        return Currency.UNKNOWN
