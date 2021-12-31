import abc
from datetime import date

from mabooia import lazy, Rational
from mabooia.accounting import Currency


class StockExchange:
    def __init__(self, _id: str, name: str, location):
        self._id = _id
        self._name = name
        self._location = location

    def __str__(self):
        return self.id

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def location(self):
        return self._location


########################################

class Security(abc.ABC):
    def __init__(self, symbol: str, currency: Currency):
        self._symbol = symbol
        self._currency = currency

    @property
    def symbol(self) -> str:
        return self._symbol

    @property
    def currency(self) -> Currency:
        return self._currency

    @property
    @abc.abstractmethod
    def shares_per_unit(self):
        pass


class Stock(Security):
    def __init__(self, symbol: str, currency: Currency, stock_exchange: StockExchange = None):
        Security.__init__(self, symbol, currency)
        self._stock_exchange = stock_exchange

    def __str__(self):
        stx = self.stock_exchange.id + ':' if self.stock_exchange is not None else ''
        return f"{stx}{self.symbol}"

    @property
    def stock_exchange(self):
        return self._stock_exchange

    @property
    def shares_per_unit(self):
        return 1


class OptionContract(Security, abc.ABC):
    def __init__(self, stock: Stock, exp_date: date, strike_price: Rational):
        self._stock = stock
        self._exp_date = exp_date
        self._strike_price = strike_price
        Security.__init__(self, self.symbol, stock.currency)

    def __str__(self):
        return self.symbol

    @property
    def shares_per_unit(self):
        return 100

    @property
    def symbol(self):
        return f"{self.stock.symbol}{self.exp_date.strftime('%Y%b%d')}" \
               f"@{'{0:g}'.format(self.strike_price)}{self.option_type}"

    @property
    def stock(self) -> Stock:
        return self._stock

    @property
    def exp_date(self) -> date:
        return self._exp_date

    @property
    def strike_price(self) -> Rational:
        return self._strike_price

    @property
    def is_call(self) -> bool:
        return isinstance(self, CallOption)

    @property
    def is_put(self) -> bool:
        return isinstance(self, PutOption)

    @property
    @abc.abstractmethod
    def option_type(self) -> str:
        pass


class CallOption(OptionContract):
    def __init__(self, stock: Stock, exp_date: date, strike_price: Rational):
        OptionContract.__init__(self, stock, exp_date, strike_price)

    @property
    def option_type(self) -> str:
        return 'CALL'


class PutOption(OptionContract):
    def __init__(self, stock: Stock, exp_date: date, strike_price: Rational):
        OptionContract.__init__(self, stock, exp_date, strike_price)

    @property
    def option_type(self) -> str:
        return 'PUT'


########################################

def _get_stock_exchanges():
    exchanges = [
        StockExchange('NSDAQ', 'Nasdaq Stock Exchange', 'New York, USA'),
        StockExchange('NYSE', 'New York Stock Exchange', 'New York, USA'),
        StockExchange('IEX', 'Investors Exchange', 'New York, USA'),
        StockExchange('BOX', 'Boston Options Exchange, LLC', 'Boston, USA'),
        StockExchange('CHX', 'Chicago Stock Exchange', 'Chicago, USA'),
        StockExchange('BATS', 'Bats Global Market', 'Lenexa, USA'),
        StockExchange('TSX', 'Toronto Stock Exchange', 'Toronto, Canada'),
        StockExchange('CDNX', 'Canadian Venture Exchange', 'Calgary, Canada'),
    ]

    res = dict()
    for ex in exchanges:
        res[ex.id] = ex
    return res


_stock_exchanges = lazy(_get_stock_exchanges)


def all_stock_exchanges() -> dict:
    return _stock_exchanges.get()


def get_stock_exchange(_id: str) -> StockExchange:
    return all_stock_exchanges()[_id]
