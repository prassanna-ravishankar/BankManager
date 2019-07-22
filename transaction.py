import re
import dateutil.parser
import ccy
import logging
from basebank import BankException, BankAccountID

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
        assert amount >= 0, "Cannot transfer negative amounts. " \
                            "Stop gaming the system!"

        self._date = dateutil.parser.parse(date)
        self._source = BankAccountID(source)
        self._destination = BankAccountID(destination)
        self._amount = amount
        self._id = transaction_id

        currency_obj = ccy.currency(currency)
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
        return (self._source.bankid ==
                self._destination.bankid)

    # Helper functions to determine if the transaction is an incoming
    # or an outgoing transaction with Respect to a reference_bank_code
    def is_outgoing(self, reference_bank_code):
        if self.internal:
            return False
        else:
            return reference_bank_code == self._source.bankid

    def is_incoming(self, reference_bank_code):
        if self.internal:
            return False
        else:
            return reference_bank_code == self._destination.bankid

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



class TransactionList(object):
    """
    Defines a list of transactions, bank specific
    """
    def __init__(self, bank):
        """
        Starts from an empty transaction list per bank
        Parameters
        ----------
        bank : instance of Bank
            Each transaction list is unique to a bank.
        """
        self._transactions = []
        self._bank = bank

    def add_transaction(self, *args, **kwargs):
        """
        Constructs a Transaction instance and pushes it
        Refer to Transaction.__init__(...) for parameters
        """
        self._transactions.append(
            Transaction(*args, **kwargs)
        )
