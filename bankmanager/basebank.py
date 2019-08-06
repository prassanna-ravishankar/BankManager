import re
import logging
import datetime
from bankmanager import config

logger = logging.getLogger(__name__) # Make a logger for this class


class BankCode(object):
    def __init__(self, bankid):
        assert len(bankid) == 4 # Early reject
        assert len(re.findall(config.BANK_ID_RULE, bankid)) == 1  #Some regex to assert the right format
        self._bankid = bankid

    @property
    def bankid(self):
        return self._bankid

    @bankid.setter
    def bankid(self, value):
        logger.debug("Cannot change bankid")
        pass

    def __str__(self):
        return self._bankid


class BankZone(object):
    def __init__(self, timezone):
        basic_split = timezone.split("UTC")
        assert len(basic_split) == 2, "Not the expected format"
        hours, minutes = [int(part) for part in basic_split[1].split(":")]
        if hours < 0:
            minutes *= -1
        self._timezone = datetime.timezone(datetime.timedelta(hours=hours,
                                                              minutes=minutes))

    def __str__(self):
        tzname = self._timezone.__str__()
        if tzname == "UTC":
            tzname+="+00:00"
        return tzname

    @property
    def timezone(self):
        return self._timezone

    @timezone.setter
    def timezone(self,value):
        logger.debug("Hope you have a great time in your new location!")
        self._timezone = BankZone(timezone=value)


class BankAccountID(object):
    def __init__(self, accountid, bankid=None):
        self._accountid = None

        # Screw the dashes first
        accountid = "".join(accountid.split("-"))

        if bankid is None:
            assert len(re.findall("^[0-9A-F]{32}$", accountid)) == 1
            self._bankid = BankCode(accountid[0:4])
            self._accountid = accountid[5:]
        else:
            assert len(re.findall("^[0-9A-F]{28}$", accountid)) == 1
            assert(issubclass(type(accountid), BankCode)), \
                "This parameter has to be an instance of Bankid or None"
            self._bankid = bankid
            self._accountid = accountid

    @property
    def id(self):
        return self._bankid + self._accountid

    @id.setter
    def id(self, value):
        logger.debug("Cannot reset id")

    @property
    def bankid(self):
        return self._bankid
    
    @property
    def accountid(self):
        return self._accountid

    def __str__(self):
        return self._bankid.bankid + self._accountid[0:4] + "-" + \
               self._accountid[4:8] + "-" + self._accountid[8:12] + "-" + \
               self._accountid[12:16] + "-" + self._accountid[16:]


# Creating a custom Exception so we don't mix it with primitive exceptions
class BankException(Exception):
    pass


if __name__ == "__main__":
    # Sandbox
    working_id = BankCode("BB01")
    print(working_id)
    # not_working_id = BankCode("b0123")
    # print (not_working_id)
    # another_not_working = BankCode("cc01")
    # print(another_not_working)

    working_zone = BankZone("UTC-3:30")
    print(working_zone)
    anotherworking_zone = BankZone("UTC+00:00")
    print(anotherworking_zone)
    # nonworking_zone = BankZone("UTC")

    working_account = BankAccountID("BB021234-5678-9012-3456-789012345678")
    print(working_account)

