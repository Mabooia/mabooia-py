import datetime
from datetime import date

from mabooia import rat, Rational
from mabooia.accounting import Currency

import mabooia.finance as fin
from mabooia.finance import OptionExpiration


class QuestradeTransaction:
    @staticmethod
    def to_date(str_date: str) -> date:
        date_format = "%Y-%m-%d %H:%M:%S %p"
        return datetime.datetime.strptime(str_date, date_format).date()

    def __init__(self, obj):
        self.obj = obj

    def __str__(self):
        return str(self.obj)

    @property
    def acc_id(self) -> str:
        return self.obj["Account #"]

    @property
    def acc_type(self) -> str:
        return self.obj["Account Type"]

    @property
    def transaction_date(self) -> date:
        return self.to_date(self.obj["Transaction Date"])

    @property
    def settlement_date(self) -> date:
        return self.to_date(self.obj["Settlement Date"])

    @property
    def description(self) -> str:
        return self.obj["Description"]

    @property
    def action(self):
        return self.obj["Action"]

    @property
    def symbol(self):
        return self.obj["Symbol"]

    @property
    def quantity(self) -> Rational:
        return rat(self.obj["Quantity"])

    @property
    def price(self) -> Rational:
        return rat(self.obj["Price"])

    @property
    def gross_amount(self) -> Rational:
        return rat(self.obj["Gross Amount"])

    @property
    def commission(self) -> Rational:
        return rat(self.obj["Commission"])

    @property
    def net_amount(self) -> Rational:
        return rat(self.obj["Net Amount"])

    @property
    def currency(self) -> Currency:
        return Currency[self.obj["Currency"].upper()]

    @property
    def activity_type(self):
        return self.obj["Activity Type"]

    def to_event(self):
        action = self.action.lower()
        acc_id = self.acc_id
        security = self.get_security()
        td = self.transaction_date
        sd = self.settlement_date
        fee = abs(self.commission)
        q = abs(self.quantity)

        if action == 'div':
            return fin.Dividend(acc_id, td, sd, security, self.net_amount)
        elif action == 'exp':
            return OptionExpiration(acc_id, td, sd, security, q)
        elif action == 'buy':
            return fin.Trade(acc_id, td, sd, security, q, self.price, fee)
        elif action == 'sell':
            return fin.Trade(acc_id, td, sd, security, -q, self.price, fee)
        else:
            return fin.UnknownEvent(acc_id, td, sd, self)

    def is_call(self):
        return self.description.startswith('CALL ')

    def is_put(self):
        return self.description.startswith('PUT ')

    def is_option(self):
        return self.is_call() or self.is_put()

    def get_security(self):
        if self.is_option():
            d = self._get_option_data()
            stock = fin.Stock(d['stock_symbol'], self.currency)
            if self.is_call():
                return fin.CallOption(stock, d['exp_date'], d['strike_price'])
            elif self.is_put():
                return fin.PutOption(stock, d['exp_date'], d['strike_price'])
            else:
                raise ValueError
        else:
            return fin.Stock(self.symbol, self.currency)

    def _get_option_data(self):
        data = self._get_option_data_from_symbol()
        return data if data is not None else self._get_option_data_from_desc()

    def _get_option_data_from_symbol(self):
        pattern = fin.from_tmpl('^:stock::day::month::year::opt_type::price:')
        return fin.get_option_dict(pattern, self.symbol)

    def _get_option_data_from_desc(self):
        pattern = fin.from_tmpl('^:opt_type: :stock: :month:/:day:/:year: :price: .*')
        return fin.get_option_dict(pattern, self.description)


class ScotiaITradeTransaction:
    @staticmethod
    def to_date(str_date: str) -> date:
        date_format = "%d-%b-%y"
        return datetime.datetime.strptime(str_date, date_format).date()

    def __init__(self, obj, account_id):
        self.obj = obj
        self._account_id = account_id

    @property
    def account_id(self):
        return self._account_id

    @property
    def transaction_date(self) -> date:
        return self.to_date(self.obj["Transaction Date"])

    @property
    def settlement_date(self) -> date:
        return self.to_date(self.obj["Settlement Date"])

    @property
    def symbol(self):
        return self.obj['Symbol']

    @property
    def description(self):
        return self.obj['Description']

    @property
    def currency(self):
        return Currency[self.obj['Account Currency'].upper()]

    @property
    def type(self):
        return self.obj['Type']

    @property
    def quantity(self) -> Rational:
        return rat(self.obj['Quantity'])

    @property
    def price(self) -> Rational:
        return rat(self.obj['Price'])

    @property
    def settlement_amount(self) -> Rational:
        return rat(self.obj['Settlement Amount'])

    def to_event(self):
        action = self.type.lower()
        acc_id = self.account_id
        td = self.transaction_date
        sd = self.settlement_date
        q = abs(self.quantity)
        price = self.price
        amt = abs(self.settlement_amount)
        stock = fin.Stock(self.symbol, self.currency)

        if action == 'cash div':
            return fin.Dividend(acc_id, td, sd, stock, amt)
        elif action == 'buy':
            if self.price == 0:
                # REI on DRIPs
                return fin.Trade(acc_id, td, sd, stock, q, amt / q, Rational.zero())
            else:
                # Normal buy
                fee = amt - q * price
                return fin.Trade(acc_id, td, sd, stock, q, price, fee)
        elif action == 'sell':
            fee = q * price - amt
            return fin.Trade(acc_id, td, sd, stock, -q, price, fee)
        else:
            return fin.UnknownEvent(acc_id, td, sd, self)
