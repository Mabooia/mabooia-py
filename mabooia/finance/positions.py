from mabooia import lazy, Rational
from mabooia.accounting import Currency
from mabooia.collections.mutable import LinkedList
from mabooia.crypto import sha256_to_str
from mabooia.finance import Trade, Security


class Position:
    def __init__(self, account_id: str, security: Security):
        self._account_id = account_id
        self._security = security
        self._events = LinkedList()
        self._lazy_id = lazy(self._get_id)
        self._quantity = Rational(0)
        self._avg_cost = Rational(0)
        self._realized_pl = Rational(0)

    def __str__(self):
        ff = '{0:,g}'
        realized_pl_text = f" | Realized P/L: {ff.format(self.realized_pl)} {self.currency}"\
            if self.realized_pl != 0\
            else ''

        if self.is_closed:
            return f"{self.id[:8]}: Closed Position {self.symbol}{realized_pl_text}"

        pos_type = "Long" if self.is_long else "Short"
        return f"{self.id[:8]}: {pos_type} Position {self.symbol} * {ff.format(self.quantity)}" \
               f" Avg Cost: {ff.format(self.avg_cost)} {self.currency}" \
               f" Book Value: {ff.format(self.book_value)} {self.currency} (including fees)" \
               f"{realized_pl_text}"

    @property
    def id(self) -> str:
        return self._lazy_id.get()

    @property
    def account_id(self):
        return self._account_id

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
    def quantity(self) -> Rational:
        return self._quantity

    @property
    def events(self):
        return self._events.to_list()

    @property
    def avg_cost(self) -> Rational:
        return self._avg_cost

    @property
    def book_value(self) -> Rational:
        return self.quantity * self.avg_cost * self.security.shares_per_unit

    @property
    def realized_pl(self) -> Rational:
        return self._realized_pl

    @property
    def is_closed(self):
        return self.quantity == 0

    @property
    def is_open(self):
        return self.quantity != 0

    @property
    def is_long(self):
        return self.quantity > 0

    @property
    def is_short(self):
        return self.quantity < 0

    def add_event(self, event: Trade):
        qty = self.quantity
        avg_cost = self.avg_cost
        book_val = self.book_value
        shares_per_unit = self.security.shares_per_unit

        if isinstance(event, Trade):
            decreasing_position = (qty > 0 and event.is_sell) or (qty < 0 and event.is_buy)
            qty += event.quantity
            if decreasing_position:
                self._realized_pl += -event.quantity * shares_per_unit * (event.price - avg_cost) - event.fee
                book_val = qty * shares_per_unit * avg_cost
            else:
                book_val -= event.total_vector

        self._quantity = qty
        self._avg_cost = book_val / (qty * shares_per_unit) if qty != 0 else 0
        self._events.append(event)

    def _get_id(self):
        keys = [
            str(self.__class__),
            str(self.symbol),
            str(self.currency),
        ]

        return sha256_to_str(keys)
