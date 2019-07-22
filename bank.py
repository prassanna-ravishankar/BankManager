from basebank import BankZone, BankCode


class Bank(object):
    def __init__(self, code, timezone, name=""):
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
        self._name = name
