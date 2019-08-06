#!/usr/bin/env python3
# system modules
import random
import csv
import os
import datetime
from iso4217 import Currency
import argparse

# Fetched modules for testing
from faker import Faker
from rstr import xeger
from faker.providers import BaseProvider
import pytz
import logging

# My modules
from bankmanager.transaction import Transaction
from bankmanager import config
from bankmanager.currencyrates import CurrencyRateList

# Store currencies in this dict
CURRENCY_LIST = CurrencyRateList()

# Logger coz why not
logger = logging.getLogger("Fake Data Generator")


class TransactionProvider(BaseProvider):
    def __init__(self, generator):
        BaseProvider.__init__(self, generator)
        self._internal_faker = Faker()

    @staticmethod
    def bank_id():
        return xeger(config.BANK_ID_RULE)

    def bank_name(self):
        return self._internal_faker.name().split(' ')[0] + " Bank"

    def timezone_str(self):
        tzone = pytz.timezone(self._internal_faker.timezone()).localize(
            datetime.datetime.now()
        ).strftime('%z')
        return tzone[0:3] + ":" + tzone[3:]

    def utc_timezone(self):
        return "UTC" + self.timezone_str()

    def date_str(self, tzone=None):
        if tzone is None:
            return self._internal_faker.iso8601() + self.timezone_str()
        else:
            return self._internal_faker.iso8601() + tzone

    def _gen_agnostic_data(self, date=None):
        if date is None:
            date = self.date_str()
        amount = str(abs(self._internal_faker.pyfloat()))
        currency = random.choice(list(Currency.__members__.values())).code
        category = self._internal_faker.name().split(' ')[0]

        # Before we go, lets set the rate of that currency
        # if its previously set, do not reset it
        # CurrencyList handles BaseCurrency modifications
        currency_rate = random.randint(0, 100)
        CURRENCY_LIST.add_currency_at_date(
            currency,
            currency_rate,
            date
        )

        return date, amount, currency, category

    @staticmethod
    def _gen_transaction(bankid, incoming=True, outgoing=False,
                         other_bank_id=None):
        if not other_bank_id:
            other_bank_id = xeger(config.BANK_ID_RULE)
        if incoming:
            dest_id = bankid + xeger(config.BANKLESS_ACCOUNT_RULE)
        else:
            dest_id = other_bank_id + xeger(config.BANKLESS_ACCOUNT_RULE)

        if outgoing:
            source_id = bankid + xeger(config.BANKLESS_ACCOUNT_RULE)
        else:
            source_id = other_bank_id + xeger(config.BANKLESS_ACCOUNT_RULE)

        transaction_id = xeger(config.BANK_ACCOUNT_RULE)
        return transaction_id, source_id, dest_id

    def transaction(self, bankid, other_bank_id=None, date=None):
        date, amount, currency, category = self._gen_agnostic_data(date=date)

        # Randomly choose the type of the transaction
        transaction_id, source_id, dest_id = \
            random.choice(
                [
                    # Internal Transaction
                    self._gen_transaction(bankid, True, True, other_bank_id),

                    # Outgoing Transaction
                    self._gen_transaction(bankid, False, True, other_bank_id),

                    # Incoming Transaction
                    self._gen_transaction(bankid, True, False, other_bank_id)

                ]
            )

        if Transaction(
                date, source_id, dest_id, transaction_id,
                amount, currency, category
        ).internal:
            other_bank_id = None

        return date, transaction_id, source_id, \
               dest_id, amount, currency, category, other_bank_id

    @staticmethod
    def random_transaction(self):
        rule_gen_id = r'^[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-' \
                      r'[0-9A-F]{4}-[0-9A-F]{12}$'
        transaction_id = xeger(rule_gen_id)
        source_id = xeger(rule_gen_id)
        dest_id = xeger(rule_gen_id)
        date, amount, currency, category = self._gen_agnostic_data()
        return date, transaction_id, source_id, dest_id, amount, currency, category


def generate_multiple_transactions(nr_entries):
    transaction_faker = Faker()
    transaction_faker.add_provider(TransactionProvider)
    bid = transaction_faker.bank_id()
    return [",".join(transaction_faker.transaction(bid)) + "\n"
            for n in range(0, nr_entries)], bid


def fake_bank_transactions(bank_id=None, filename=None, date=None, logsize=10,
                           pending_transactions={}, other_bank_id=None):
    transaction_faker = Faker()
    transaction_faker.add_provider(TransactionProvider)
    if date is None:
        date = transaction_faker.date_str()
    if bank_id is None:
        bank_id = transaction_faker.bank_id()
    if filename is None:
        # Generate with the bank as the filename
        filename = str(bank_id) + ".csv"
    with open(filename, 'w') as f:
        writer = csv.writer(f)
        for n in range(0, logsize):
            date, transaction_id, source_id, dest_id, amount, currency, \
            category, other_bank_id = \
                transaction_faker.transaction(bank_id, other_bank_id, date)
            if other_bank_id:
                if other_bank_id not in pending_transactions:
                    pending_transactions[other_bank_id] = []
                pending_transactions[other_bank_id].append((date, transaction_id,
                                                            source_id, dest_id,
                                                            amount, currency,
                                                            category))
            writer.writerow((date, transaction_id, source_id,
                            dest_id, amount, currency, category))


def write_pending_transactions(filename, pending_bank_transactions):
    transaction_faker = Faker()
    transaction_faker.add_provider(TransactionProvider)
    with open(filename, 'w') as f:
        writer = csv.writer(f)
        for pending_transaction in pending_bank_transactions:
            date, transaction_id, source_id, dest_id, amount, currency, \
            category = pending_transaction
            writer.writerow((date, transaction_id, source_id,
                            dest_id, amount, currency, category))


def fake_multibank_transactions(nr_banks=10, entries_per_bank=10,
                                logsize=10, output_folder="./",
                                currency_file="currency_rates.json"):
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)
    transaction_faker = Faker()
    transaction_faker.add_provider(TransactionProvider)
    with open(os.path.join(output_folder, "transactions.csv"), "w") as f:
        writer = csv.writer(f)
        bank_data = [(
            transaction_faker.bank_id(),
            transaction_faker.utc_timezone(),
            transaction_faker.bank_name()
        )
            for bankidx in range(nr_banks)]
        bank_data_dict = {b[0]: {"tzone": b[1], "name": b[2]} for b in bank_data}
        pending_transactions = {}
        for bank_code, timezone, bank_name in bank_data:
            logger.info("On Bank:" + bank_code)
            for entry_idx in range(entries_per_bank):
                tzone = timezone.split("UTC")[-1]
                date = transaction_faker.date_str(tzone)

                # Other bank
                other_bank_id = random.choice(list(bank_data_dict.keys()))

                # A convention because why not
                filename_local = bank_code + '_' + \
                                 '{0:04.0f}'.format(entry_idx) + \
                                 ".csv"
                filename = os.path.join(
                    output_folder,
                    filename_local
                )
                fake_bank_transactions(bank_code, filename, date,
                                       logsize=logsize,
                                       pending_transactions=pending_transactions,
                                       other_bank_id=other_bank_id)
                writer.writerow(
                    [
                        date,
                        bank_code,
                        timezone,
                        filename_local,
                        bank_name
                    ]
                )

        logger.info("Filling up some pending transactions")
        # Fill up the pending transactions
        for bank_code in list(pending_transactions.keys()):
            logger.info("Processing pending txns for :" + bank_code)
            # check if bank already present
            if bank_code in bank_data_dict.keys():
                tzone = bank_data_dict[bank_code]["tzone"]
                name = bank_data_dict[bank_code]["name"]

            # If not, create it
            else:
                tzone = transaction_faker.utc_timezone()
                name = transaction_faker.bank_name()
                bank_data_dict[bank_code] = {
                    "tzone": tzone,
                    "name": name
                }

            date = transaction_faker.date_str()
            filename_local = str(bank_code) + "_pending.csv"

            filename = os.path.join(
                output_folder,
                filename_local
            )
            write_pending_transactions(filename,
                                       pending_transactions[bank_code])
            writer.writerow(
                [
                    date,
                    bank_code,
                    tzone,
                    filename_local,
                    name
                ]
            )
    CURRENCY_LIST.dump(os.path.join(output_folder,
                                    currency_file))
    pass


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Generate fake bank data "
                                                 "with currency rates too")
    parser.add_argument("-t", "--transaction_folder", type=str,
                        help="What is the transaction folder",
                        default="./transactions")
    parser.add_argument("-c", "--currency_rates", type=str,
                        default=None,
                        help="The name of the currency rates file")
    parser.add_argument("-b", "--banks", type=int,
                        default=10,
                        help="Number of banks")
    parser.add_argument("-e", "--entries", type=int,
                        default=10,
                        help="Number of logs per bank")
    parser.add_argument("-l", "--logsize", type=int,
                        default=10,
                        help="Number of transactions per log")
    args = parser.parse_args()
    transaction_folder = os.path.abspath(args.transaction_folder)
    fake_multibank_transactions(nr_banks=args.banks,
                                entries_per_bank=args.entries,
                                logsize=args.logsize,
                                output_folder=transaction_folder,
                                currency_file=args.currency_rates)
