from faker import Faker
from rstr import xeger
from faker.providers import BaseProvider
import random
import csv
import os
import pytz
import datetime
from iso4217 import Currency
from decimal import Decimal
import json
from transaction import Transaction

# Store currencies in this dict
# TODO : or not, currently not handling changing currency rates with time
global_currency_rates = {}


class TransactionProvider(BaseProvider):
    def __init__(self, generator):
        BaseProvider.__init__(self, generator)
        self._internal_faker = Faker()

    @staticmethod
    def bank_id():
        return xeger(r"[0-9A-F]{4}")

    def bank_name(self):
        return self._internal_faker.name().split(' ')[0] + " Bank"

    def timezone(self):
        tzone = pytz.timezone(self._internal_faker.timezone()).localize(
            datetime.datetime.now()
        ).strftime('%z')
        return "UTC" + tzone[0:3] + ":" + tzone[3:]

    def date_str(self):
        return self._internal_faker.iso8601()

    def _gen_agnostic_data(self, date=None):
        if date is None:
            date = self.date_str()
        amount = str(abs(self._internal_faker.pyfloat()))
        currency = random.choice(list(Currency.__members__.values())).code
        category = self._internal_faker.name().split(' ')[0]

        # Before we go, lets set the rate of that currency
        # if its previously set, do not reset it
        if currency not in global_currency_rates:
            if currency is "USD":
                currency_rate = 1
            else:
                currency_rate = Decimal(random.randint(0, 100))
                global_currency_rates[currency] = str(currency_rate)

        return date, amount, currency, category

    @staticmethod
    def _gen_transaction(bankid, incoming=True, outgoing=False):
        general_rule = r'^[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-' \
                       r'[0-9A-F]{4}-[0-9A-F]{12}$'
        my_bank_rule = r'^[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-' \
                       r'[0-9A-F]{4}-[0-9A-F]{12}$'
        if incoming:
            dest_id = bankid + xeger(my_bank_rule)
        else:
            dest_id = xeger(general_rule)

        if outgoing:
            source_id = bankid + xeger(my_bank_rule)
        else:
            source_id = xeger(general_rule)

        transaction_id = xeger(general_rule)
        return transaction_id, source_id, dest_id

    def transaction(self, bankid, date=None, pending_transactions={}):
        date, amount, currency, category = self._gen_agnostic_data(date=date)

        # Randomly choose the type of the transaction
        transaction_id, source_id, dest_id = \
            random.choice(
                [
                    # Internal Transaction
                    self._gen_transaction(bankid, True, True),

                    # Outgoing Transaction
                    self._gen_transaction(bankid, False, True),

                    # Incoming Transaction
                    self._gen_transaction(bankid, True, False)

                ]
            )

        transaction_instance = Transaction(
            date, source_id, dest_id, transaction_id,
            amount, currency, category
        )
        other_bank_id = None
        if not transaction_instance.internal:
            other_bank_id = transaction_instance.other_bank(bankid)

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
                           pending_transactions={}):
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
                transaction_faker.transaction(bank_id, date)
            if other_bank_id:
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
                                output_folder="./"):
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)
    transaction_faker = Faker()
    transaction_faker.add_provider(TransactionProvider)
    with open(os.path.join(output_folder, "transactions.csv"), "w") as f:
        writer = csv.writer(f)
        bank_data = [(
            transaction_faker.bank_id(),
            transaction_faker.timezone(),
            transaction_faker.bank_name()
        )
            for bankidx in range(nr_banks)]
        pending_transactions = {bankid:[] for bankid, tz, bname in bank_data}
        for bank_code, timezone, bank_name in bank_data:
            # bank_code = transaction_faker.bank_id()
            # timezone = transaction_faker.timezone()
            # bank_name = transaction_faker.bank_name()
            for entry_idx in range(entries_per_bank):
                date = transaction_faker.date_str()
                filename_local = bank_code + '_' + \
                                 '{0:04.0f}'.format(entry_idx) + ".csv"
                filename = os.path.join(
                    output_folder,
                    filename_local
                )
                fake_bank_transactions(bank_code, filename, date,
                                       pending_transactions=pending_transactions)
                writer.writerow(
                    [
                        date,
                        bank_code,
                        timezone,
                        filename_local,
                        bank_name
                    ]
                )

        # Fill up the pending transactions
        for bank_code, timezone, bank_name in bank_data:
            date = transaction_faker.date_str()
            filename_local = str(bank_code) + "_pending.csv"
            bank_name = None

            filename = os.path.join(
                output_folder,
                filename_local
            )
            write_pending_transactions(filename, pending_transactions[bank_code])
            writer.writerow(
                [
                    date,
                    bank_code,
                    timezone,
                    filename_local,
                    bank_name
                ]
            )
            pass
    # By this time a unique set of currency rates will be generated.
    json.dump(global_currency_rates,
              open(os.path.join(output_folder, "currency_rates.json"), "w")
              )
    pass


if __name__ == "__main__":
    import time
    start = time.time()
    fake_multibank_transactions(output_folder="transactions/")
    duration = (time.time() - start)
    print("Duration: ", duration)

