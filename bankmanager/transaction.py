import re
import dateutil.parser
from itertools import groupby
from iso4217 import Currency
import logging
from bankmanager.basebank import BankException, BankAccountID
from bankmanager import config

logger = logging.getLogger(__name__)


class Transaction(object):
    def __init__(self, date, source, destination, transaction_id,
                 amount=0, currency="USD", category=None):
        """
        A container which represents a transaction which basically records
        a transaction from a particular account ID to a particular account ID

        Bank specific details are not described because that can
        be inferred from the acocunt details

        Also has a property to quickly determine whether is an internal transaction

        External Transactions : outgoing or incoming

        Parameters
        ----------
        date : str,
            Date in ISO-8061 format.
        source : str,
            Where is the transaction coming from?
            Where is the transaction coming from?
        destination : str,
            Where is the transaction going?
        transaction_id : str,
            An ID for the transaction
        amount : float,
            Amount to transfer. Default = 0
        currency : str,
            Which currency to transfer. Default :  USD
        category : str,
            Some human readable note to attach to the transfer
        """
        assert float(amount) >= 0, "Cannot transfer negative amounts. "\
                                   "Stop gaming the system!"

        self._date = dateutil.parser.parse(date)
        self._source = BankAccountID(source)
        self._destination = BankAccountID(destination)
        self._amount = float(amount)
        self._id = transaction_id

        currency_obj = Currency(currency)
        if currency_obj is not None:
            self._currency = currency_obj
        else:
            logger.debug("Cannot parse currency, Raising an error")
            raise BankException("Currency Parse error")

        self._category = None
        if category is not None:
            assert len(re.findall("^[0-9A-Za-z_.-]*$", category)) == 1, \
                "Category contains unnacceptable charecters"
            self._category = category

    @property
    def internal(self):
        return (self._source.bankid.bankid ==
                self._destination.bankid.bankid)

    # Helper functions to determine if the transaction is an incoming
    # or an outgoing transaction with Respect to a reference_bank_code
    def is_outgoing(self, reference_bank_code):
        if self.internal:
            return False
        else:
            return reference_bank_code.bankid == self._source.bankid.bankid

    def is_incoming(self, reference_bank_code):
        if self.internal:
            return False
        else:
            return reference_bank_code.bankid == self._destination.bankid.bankid

    def concerns_bank(self, reference_bank_code):
        """
        Utility function to check if a given transaction belongs to a given bank
        -- Has to be one or both of [incoming, outgoing] belongs to the bank,
         as a bank owns its transaction log which has a list of its transactions
        Parameters
        ----------
        reference_bank_code

        Returns
        -------

        """
        return (self._destination.bankid == reference_bank_code) or \
               (self._source.bankid == reference_bank_code)

    def other_bank(self, bankid):
        assert not self.internal, \
            "This function is only called on external transactions"
        if self._source.bankid.bankid == bankid:
            return self._destination.bankid.bankid
        if self._destination.bankid.bankid == bankid:
            return self._source.bankid.bankid

    @property
    def currency_code(self):
        return self._currency.code

    @property
    def category(self):
        return self._category

    @property
    def transaction_time(self):
        return self._date.isoformat()

    @property
    def transaction_timezone(self):
        return self.transaction_time[-6:]

    @property
    def transaction_amount_nocurrency(self):
        return self._amount

    @property
    def transaction_date(self):
        return dateutil.parser.parse(self.transaction_time).date().isoformat()


class TransactionList(object):
    """
    Defines a list of transactions, bank specific
    """
    def __init__(self, bank, currency_rates=None):
        """
        Starts from an empty transaction list per bank
        Parameters
        ----------
        bank : instance of Bank
            Each transaction list is unique to a bank.

        currency_rates: instance of CurrencyRateList
            Required to calculate the balance in a unified currency
        """
        self._transactions = []
        self._transaction_categories = set()
        self._bank = bank
        self._currencies = []
        self._base_currency = None
        self._amount = None
        self._dates = set()
        self._currency_rates = currency_rates

    def add_transaction(self, *args, **kwargs):
        """
        Constructs a Transaction instance and pushes it
        Refer to Transaction.__init__(...) for parameters
        """
        my_transaction = Transaction(*args, **kwargs)
        self._transactions.append(
            my_transaction
        )
        self._currencies.append(my_transaction.currency_code)
        self._transaction_categories.add(my_transaction.category)
        self._dates.add(
            dateutil.parser.parse(
                my_transaction.transaction_time
            ).date().isoformat())

    def append(self, transaction):
        """
        different from add_transaction in the sense that it doesn't
        instantiate a transaction but just appends it onto the list
        """
        self._transactions.append(
            transaction
        )
        self._currencies.append(transaction.currency_code)
        self._transaction_categories.add(transaction.category)
        self._dates.add(
            dateutil.parser.parse(
                transaction.transaction_time
            ).date().isoformat())

    def currencies(self):
        return {key: len(list(group)) for key, group in groupby(self._currencies)}

    def calculate_balance(self, currency_rates=None):
        """
        Calculates balance in the base currency
        """
        if currency_rates is None:
            currency_rates = self._currency_rates
        assert currency_rates is not None, \
            "Cannot calculate the balances without date-wise currency rates"
        self._amount = 0
        incoming_amount = 0
        incoming_count = 0
        outgoing_amount = 0
        outgoing_count = 0
        internal_count = 0
        for tx in self._transactions:
            if tx.currency_code == config.BASE_CURRENCY:
                rate = 1
            else:
                rate = currency_rates.currency_rate_at_date(
                    tx.currency_code,
                    tx.transaction_time
                )
            if rate is None:
                logger.info("We are parsing a currency, whose"
                            " rate is not defined at that time. "
                            "Assuming as if it is USD")
            if tx.internal:
                internal_count += 1
                continue
            elif tx.is_outgoing(self.bank.code):
                # self._amount -= tx.transaction_amount_nocurrency * rate
                outgoing_amount += tx.transaction_amount_nocurrency * rate
                outgoing_count += 1
            elif tx.is_incoming(self.bank.code):
                # self._amount += tx.transaction_amount_nocurrency * rate
                incoming_amount += tx.transaction_amount_nocurrency * rate
                incoming_count += 1
            else:
                assert 1 == 0, "Every transaction has to be internal "\
                               "or incoming or outgoing"
        self._amount = incoming_amount - outgoing_amount
        return (incoming_amount, incoming_count), \
               (outgoing_amount, outgoing_count), \
               internal_count

    @property
    def currency_rates(self):
        return self._currency_rates

    @property
    def categories(self):
        return self._transaction_categories

    @property
    def balance(self):
        if self._amount is None:
            self.calculate_balance()
        return self._amount

    @property
    def bank(self):
        return self._bank

    @property
    def transactions(self):
        return self._transactions

    @property
    def dates(self):
        return self._dates

    @classmethod
    def categorize(cls, transaction_list):
        categorized_transactions = {date: cls(transaction_list.bank,
                                              transaction_list.currency_rates)
                                    for date in transaction_list.categories}
        for curr_transaction in transaction_list.transactions:
            categorized_transactions[curr_transaction.category].append(
                curr_transaction
            )
        return categorized_transactions

    @classmethod
    def categorize_by_date(cls, transaction_list):
        categorized_transactions = {date: cls(transaction_list.bank,
                                              transaction_list.currency_rates)
                                    for date in transaction_list.dates}
        for curr_transaction in transaction_list.transactions:
            categorized_transactions[
                curr_transaction.transaction_date
            ].append(curr_transaction)
        return categorized_transactions



