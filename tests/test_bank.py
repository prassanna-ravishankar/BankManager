"""
This file tests the different components of bankmanager.
"""
# Path magic to get pytest to work sanely
import sys
import os
pth = os.path.dirname(__file__)
pth = os.path.join(pth, "..")
sys.path.append(pth)
import pytest
from faker import Faker
import pytz
import datetime

from bankmanager.basebank import BankCode, BankZone
from bankmanager.transaction import Transaction, TransactionList
from bankmanager.currencyrates import CurrencyRateList
from rstr import xeger
from bankmanager import config
import random
from iso4217 import Currency
from bankmanager import bank

def gen_transaction(bankid, incoming=True, outgoing=False):
    if incoming:
        dest_id = bankid + xeger(config.BANKLESS_ACCOUNT_RULE)
    else:
        dest_id = xeger(config.BANK_ACCOUNT_RULE)

    if outgoing:
        source_id = bankid + xeger(config.BANKLESS_ACCOUNT_RULE)
    else:
        source_id = xeger(config.BANK_ACCOUNT_RULE)

    transaction_id = xeger(config.BANK_ACCOUNT_RULE)
    return transaction_id, source_id, dest_id


def gen_bank_id():
    return xeger(config.BANK_ID_RULE)


def gen_timezone():
    tzone = pytz.timezone(Faker().timezone()).localize(
        datetime.datetime.now()
    ).strftime('%z')
    return tzone[0:3] + ":" + tzone[3:]


def gen_agnostic_data(currency_list, date):
    amount = str(abs(Faker().pyfloat()))
    currency = random.choice(list(Currency.__members__.values())).code
    category = Faker().name().split(' ')[0]

    # Before we go, lets set the rate of that currency
    # if its previously set, do not reset it
    # CurrencyList handles BaseCurrency modifications
    currency_rate = random.randint(0, 100)
    currency_list.add_currency_at_date(
        currency,
        currency_rate,
        date
    )
    return amount, currency, category, currency_list


def test_bank_code():
    for trials in range(0,10):
        assert BankCode(gen_bank_id()), "Bank Code cannot " \
                                                     "be instantiated"
        with pytest.raises(Exception):
            assert BankCode(xeger(config.BANK_ACCOUNT_RULE)), \
                "Bank Code should not be instantiated"


def test_bank_zone():
    for trials in range(0,10):
        tzone = pytz.timezone(Faker().timezone()).localize(
            datetime.datetime.now()
        ).strftime('%z')
        tzone = "UTC" + tzone[0:3] + ":" + tzone[3:]
        assert BankZone(tzone), "Timezone cannot be instantiated"
        shuffled_tzone = tzone
        random.shuffle(list(shuffled_tzone))
        shuffled_tzone = "".join(shuffled_tzone)
        try:
            with pytest.raises(Exception):
                assert BankZone(shuffled_tzone), \
                    "Timezone should not initialize"
        except:
            assert BankZone(shuffled_tzone),\
                "Timezone should not be instantiated"


def test_transaction():
    currency_list = CurrencyRateList()
    for trial in range(0, 10):
        currency_list = CurrencyRateList()
        date = Faker().iso8601() + gen_timezone()
        bankid = gen_bank_id()
        amount, currency, category, currency_list = \
            gen_agnostic_data(currency_list, date)
        amount = float(amount)
        # Random Transaction
        transaction_id, source_id, dest_id = gen_transaction(bankid, False, False)
        assert Transaction(
            date, source_id, dest_id, transaction_id,
            amount, currency, category
        ), "Cannot instantiate Transaction"

        # Outgoing Transaction
        transaction_id, source_id, dest_id = gen_transaction(bankid, False, True)
        assert Transaction(
            date, source_id, dest_id, transaction_id,
            amount, currency, category
        ).is_outgoing(BankCode(bankid)), "Not the right kind of transaction"

        # Incoming Transaction
        transaction_id, source_id, dest_id = gen_transaction(bankid, True, False)
        assert Transaction(
            date, source_id, dest_id, transaction_id,
            amount, currency, category
        ).is_incoming(BankCode(bankid)), "Not the right kind of transaction"

        # internal
        transaction_id, source_id, dest_id = gen_transaction(bankid, True, True)
        assert Transaction(
            date, source_id, dest_id, transaction_id,
            amount, currency, category
        ).internal, "Cannot instantiate Transaction"


def test_multiple_transactions():
    my_bankid = gen_bank_id()
    my_bank = bank.Bank(
        my_bankid,
        "UTC"+gen_timezone()
    )
    txlist1 = TransactionList(my_bank)
    txlist2 = TransactionList(my_bank)
    currency_list = CurrencyRateList()

    # Outgoing txns
    for txcount in range(0,10):
        date = Faker().iso8601() + gen_timezone()
        amount, currency, category, currency_list = \
            gen_agnostic_data(currency_list, date)
        currency = "USD" # for now
        amount = 10

        # Outgoing Transaction
        transaction_id, source_id, dest_id = gen_transaction(my_bankid, False, True)
        my_tx = Transaction(
            date, source_id, dest_id, transaction_id,
            amount, currency, category
        )
        txlist1.add_transaction(date, source_id, dest_id, transaction_id,
                                amount, currency, category)
        txlist2.append(my_tx)

    assert txlist1.calculate_balance(currency_list) == txlist2.calculate_balance(currency_list)
    assert txlist1.balance == -100

    # Incoming txns
    for txcount in range(0, 10):
        date = Faker().iso8601() + gen_timezone()
        amount, currency, category, currency_list = \
            gen_agnostic_data(currency_list, date)
        currency = "USD"  # for now
        amount = 10

        # Outgoing Transaction
        transaction_id, source_id, dest_id = gen_transaction(my_bankid, True, False)
        my_tx = Transaction(
            date, source_id, dest_id, transaction_id,
            amount, currency, category
        )
        txlist1.add_transaction(date, source_id, dest_id, transaction_id,
                                amount, currency, category)
        txlist2.append(my_tx)

    assert txlist1.calculate_balance(currency_list) == txlist2.calculate_balance(currency_list)
    assert txlist1.balance == 0

    # Internal txns
    for txcount in range(0, 10):
        date = Faker().iso8601() + gen_timezone()
        amount, currency, category, currency_list = \
            gen_agnostic_data(currency_list, date)
        currency = "USD"  # for now
        amount = 10

        # Outgoing Transaction
        transaction_id, source_id, dest_id = gen_transaction(my_bankid, True, True)
        my_tx = Transaction(
            date, source_id, dest_id, transaction_id,
            amount, currency, category
        )
        txlist1.add_transaction(date, source_id, dest_id, transaction_id,
                                amount, currency, category)
        txlist2.append(my_tx)
    assert txlist1.calculate_balance(currency_list) == txlist2.calculate_balance(currency_list)
    assert txlist1.balance == 0

    pass


def test_transactions_diff_currency():
    my_bankid = gen_bank_id()
    my_bank = bank.Bank(
        my_bankid,
        "UTC" + gen_timezone()
    )
    txlist1 = TransactionList(my_bank)
    txlist2 = TransactionList(my_bank)
    currency_list = CurrencyRateList()
    total_amount = 0
    # Outgoing txns
    for txcount in range(0, 10):
        date = Faker().iso8601() + gen_timezone()
        amount, currency, category, currency_list = \
            gen_agnostic_data(currency_list, date)
        # amount = float(amount)
        total_amount += float(amount) * currency_list.currency_rate_at_date(currency, date)
        # Outgoing Transaction
        transaction_id, source_id, dest_id = gen_transaction(my_bankid, False, True)
        my_tx = Transaction(
            date, source_id, dest_id, transaction_id,
            amount, currency, category
        )
        txlist1.add_transaction(date, source_id, dest_id, transaction_id,
                                amount, currency, category)
        txlist2.append(my_tx)

    assert txlist1.calculate_balance(currency_list) == txlist2.calculate_balance(currency_list)
    assert txlist1.balance == -total_amount

    # incoming
    for txcount in range(0, 10):
        date = Faker().iso8601() + gen_timezone()
        amount, currency, category, currency_list = \
            gen_agnostic_data(currency_list, date)
        # amount = float(amount)
        total_amount -= float(amount) * currency_list.currency_rate_at_date(currency, date)
        # Outgoing Transaction
        transaction_id, source_id, dest_id = gen_transaction(my_bankid, True, False)
        my_tx = Transaction(
            date, source_id, dest_id, transaction_id,
            amount, currency, category
        )
        txlist1.add_transaction(date, source_id, dest_id, transaction_id,
                                amount, currency, category)
        txlist2.append(my_tx)

    assert txlist1.calculate_balance(currency_list) == txlist2.calculate_balance(currency_list)
    assert txlist1.balance == -total_amount


def test_categorization():
    my_bankid = gen_bank_id()
    my_bank = bank.Bank(
        my_bankid,
        "UTC" + gen_timezone()
    )
    txlist1 = TransactionList(my_bank)
    txlist2 = TransactionList(my_bank)
    currency_list = CurrencyRateList()
    # Outgoing txns
    for txcount in range(0, 10):
        date = Faker().iso8601() + gen_timezone()
        amount, currency, category, currency_list = \
            gen_agnostic_data(currency_list, date)
        amount = float(amount)
        my_tx_type = random.choice([
            (True, True),  # Internal
            (True, False),  # Incoming
            (False, True)  # Outgoing
        ])
        # Outgoing Transaction
        transaction_id, source_id, dest_id = gen_transaction(my_bankid,
                                                             my_tx_type[0],
                                                             my_tx_type[1])
        my_tx = Transaction(
            date, source_id, dest_id, transaction_id,
            amount, currency, category
        )
        txlist1.add_transaction(date, source_id, dest_id, transaction_id,
                                amount, currency, category)
        txlist2.append(my_tx)

    # Test categorization by category
    txlist_cats = TransactionList.categorize(txlist1)
    for cat, txlist in txlist_cats.items():
        for tx in txlist.transactions:
            assert cat == tx.category, "Categorization has failed"

    for date, txlist in TransactionList.categorize_by_date(txlist1).items():
        for tx in txlist.transactions:
            assert date == tx.transaction_date, "Categorization by has failed"