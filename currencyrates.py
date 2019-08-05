from iso4217 import Currency
from config import BASE_CURRENCY
from money import xrates
import json


class CurrencyRate(object):
    def __init__(self, currency="USD", rate=1):
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
        self.currency = currency
        self.rate = float(rate)
        pass

    def in_base_currency(self, amount):
        """
        Convert amount  in whatever currency to base currency(USD)
        Returns
        -------
        amount_usd : float,
            Amount converted to USD, at that point in time.
        """
        if self.currency == BASE_CURRENCY:
            return amount
        return amount * self.rate


class CurrencyRateList(object):
    """
    Hold a list of currencies, in different times of generating.
    This currencyRateList is required because we want(!!) to calculate the
    balance/sum in a particular currency.
    """
    def __init__(self):
        self._currency_rates_by_date = {}

    def add_date_if_nonexistant(self, date):
        if date not in self._currency_rates_by_date.keys():
            self._currency_rates_by_date[date] = set([])
            # Set because We don't want to repeat values

    def append_current_rate(self, currency, date, rate):
        self.add_date_if_nonexistant(date)
        currency_inst =  CurrencyRate(currency, rate)
        if currency_inst in self._currency_rates_by_date[date]:
            return False
        self._currency_rates_by_date[date].add(
            CurrencyRate(currency, rate)
        )
        return True

    def add_currency_at_date(self, currency="USD", rate=1,
                             time="1981-09-15T00:26:36+08:00"):
        if currency == BASE_CURRENCY:
            rate = 1
        success = self.append_current_rate(currency, time, rate)
        return success

    def dump(self, filename):
        for date in self._currency_rates_by_date.keys():
            self._currency_rates_by_date[date] = {
                curr.currency: curr.rate for curr in
                self._currency_rates_by_date[date]
            }

        json.dump(self._currency_rates_by_date, open(filename, "w"))

    def currency_rate_at_date(self, currency_name, date):
        if date in self._currency_rates_by_date:
            for curr in self._currency_rates_by_date[date]:
                if curr.currency == currency_name:
                    return curr.rate
        else:
            return None

    @classmethod
    def load(cls, filename):
        currency_list = CurrencyRateList()
        json_curr_list = json.load(open(filename, "r"))
        for date in json_curr_list.keys():
            curr_date_dict = json_curr_list[date]
            for curr_name, curr_rate in curr_date_dict.items():
                currency_list.add_currency_at_date(curr_name, curr_rate, date)
        return currency_list
