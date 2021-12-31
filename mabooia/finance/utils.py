import re
from datetime import date
from time import strptime

from mabooia import rat


def from_tmpl(pattern: str) -> str:
    return pattern\
        .replace(':stock:', '(?P<stock>[A-Z.\\-]+)')\
        .replace(':day:', '(?P<day>\\d{1,2})')\
        .replace(':month:', '(?P<month>(?:\\d{1,2}|[a-zA-Z]+))')\
        .replace(':year:', '(?P<year>\\d{2,4})')\
        .replace(':opt_type:', '(?P<opt_type>(?:C(?:ALL)?|P(?:UT)?))')\
        .replace(':price:', '(?P<price>\\d+(?:.\\d+))')


def get_option_dict(pattern: str, text: str):
    m = re.match(pattern, text)
    if m:
        ot = "CALL" if 'C' in m.group('opt_type') else 'PUT'

        year = m.group('year')

        month = m.group('month')
        if re.match('[a-zA-Z]{4,}', month):
            month = strptime(month, '%B').tm_mon
        elif re.match('[a-zA-Z]{3}', month):
            month = strptime(month, '%b').tm_mon

        dt = date(
            int("20" + year if len(year) == 2 else year),
            int(month),
            int(m.group('day')),
        )

        res = dict()
        res['stock_symbol'] = m.group('stock')
        res['exp_date'] = dt
        res['strike_price'] = rat(m.group('price'))
        res['type'] = ot
        return res
    else:
        return None


def format_match_to_option_symbol(pattern: str, text: str) -> str:
    d = get_option_dict(pattern, text)
    if d:
        return f"{d['stock_symbol']}{d['exp_date'].strftime('%Y%b%d')}@{d['strike_price']}{d['type']}"
    else:
        return ''
