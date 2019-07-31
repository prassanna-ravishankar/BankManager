from iso4217 import Currency
from config import BASE_CURRENCY


class CurrencyRate(object):
    def __init__(self, currency="USD", rate=1, time="1972-08-10T02:27:43"):
        """
        Describes Currency rates.
        This is a fake container, that defines the API.
        Should be replaced by a real time date dependent rate coming from
        some online API.

        Parameters
        ----------
        currency : str,
            The iso4217 currency code
        rate: float,
            The rate ate that time with respect to config.BASE_CURRENCY
        time: str,
            The iso iso8601 time-code
        """
        self._currency = currency
        self._rate=rate
        self._time = date
        pass