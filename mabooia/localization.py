import locale


def get_locale_info(loc):
    locale.setlocale(locale.LC_ALL, loc)
    return locale.localeconv()


def get_current_locale_info():
    curr_loc = locale.getlocale()
    return get_locale_info(curr_loc)


def get_decimal_separator():
    return get_current_locale_info()['decimal_point']


def get_negative_sign():
    return get_current_locale_info()['negative_sign']


def get_thousand_separator():
    return get_current_locale_info()['thousands_sep']
