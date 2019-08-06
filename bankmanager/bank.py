from bankmanager.basebank import BankZone, BankCode


class Bank(object):
    def __init__(self, code, timezone, name=None):
        """
        Representing a banking entity.
        Parameters
        ----------
        code : str,
            Code in a string format. Will have to be able to be accepted by
            BankCode(...)
        timezone : str,
            Time zone in UTC+xx:xx format where it can be behind(-) or
            ahead(+) of utc
        name : str,
            Human readable name for the bank.
        """
        self._code = BankCode(code)
        self._timezone = BankZone(timezone)
        if name is None:
            name = "UNKNOWN"
        self._name = name

    @property
    def code(self):
        return self._code

    @property
    def code_string(self):
        return self.code.bankid

    @property
    def name(self):
        return self._name

