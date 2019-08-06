from bankmanager.basebank import BankAccountID


# Basically a wallet (can easily be blockchainified)
class BankAccount(object):
    def __init__(self, account_id, currency=None):
        assert account_id is not None # Or generate new account number
        self._id = BankAccountID(account_id)
        self._currencies = []
        self._default_currency = None
        self._last_calculated_balance = None
        self._bankid = self._id.bankid
        if currency is not None:
            self.add_currency(currency)

    def check_balance(self):
        """
        TODO :  Do some algorithm  here to check transaction records and return
                value
        TODO : Maybe some kind of cache as well,  or to get it via a push
                notification whenever we calculate bank balance
        Returns
        -------

        """
        pass

    def add_currency(self, new_currency_str=None):
        self._currencies.append(new_currency_str)

        # If its the first currency,
        # make it default
        if len(self._currencies) == 1:
            self._default_currency = new_currency_str


    def generate_new_account(self, bankid=""):
        """
        bankid : str,
            String Id of Bank
            Will construct an instance of BankCode

        Returns
        -------
        new_account : BankAccount,
            Genereates a new account, with a given bank.
        """
        pass
