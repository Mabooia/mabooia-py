from mabooia.accounting import Currency
from mabooia.collections import Stream
from mabooia.collections.mutable import put_if_absent, compute_if_absent
from mabooia.finance import Event, SecurityEvent, Position
from mabooia.reactive import Observable
from mabooia.time import Timeline, TimelineEvent, TimeCriteria, all_events


class Account(Observable):
    def __init__(self, account_id, *currencies: Currency):
        self._account_id = account_id
        self._currency_sides = dict()
        for curr in currencies:
            self._currency_sides[curr] = self._create_new_currency_side(curr)

    def __getitem__(self, item):
        assert isinstance(item, Currency)
        return self._currency_sides[item]

    def __str__(self):
        return str(self.account_id)

    @property
    def account_id(self):
        return self._account_id

    @property
    def is_multicurrency(self):
        return len(self._currency_sides) > 1

    @property
    def sides(self):
        return self._currency_sides.values()

    @property
    def positions(self):
        return Stream\
            .of(self._currency_sides.values())\
            .map(lambda acc_sd: acc_sd.positions)\
            .flatten()

    def transactions(self, criteria: TimeCriteria = all_events()) -> Stream:
        return Stream\
            .of(self._currency_sides.values())\
            .map(lambda acc_sd: acc_sd.transactions(criteria))\
            .flatten()

    def add_event(self, event: Event):
        currency = event.currency
        curr_side = compute_if_absent(
            self._currency_sides,
            currency,
            lambda: self._create_new_currency_side(currency)
        )
        curr_side.add_event(event)

    def _event_raised(self, event):
        self.notify_all(event)

    def _create_new_currency_side(self, currency: Currency):
        res = AccountCurrencySide(self, currency)
        res.subscribe(self._event_raised)
        return res


class AccountCurrencySide(Observable):
    def __init__(self, account: Account, currency: Currency):
        self._account = account
        self._currency = currency
        self._timeline = Timeline().subscribe(self._event_raised)
        self._positions = dict()

    def __str__(self):
        if self.account.is_multicurrency:
            return f"{self.account} - {self.currency}"
        else:
            return str(self.account)

    @property
    def account(self):
        return self._account

    @property
    def currency(self) -> Currency:
        return self._currency

    @property
    def positions(self):
        return Stream.of(self._positions.values())

    def transactions(self, criteria: TimeCriteria = all_events()) -> Stream:
        return self.\
            _timeline\
            .events(criteria)\
            .map(lambda ev: ev.info)

    def add_event(self, event: Event):
        self._timeline.add_event(TimelineEvent(event.transaction_date, event))
        if isinstance(event, SecurityEvent):
            position = put_if_absent(self._positions, event.symbol, Position(event.account_id, event.security))
            position.add_event(event)

    def _event_raised(self, event: TimelineEvent):
        self.notify_all(event)
