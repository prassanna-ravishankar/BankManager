from faker import Faker
from rstr import xeger
from faker.providers import BaseProvider
import random
import csv

# TODO: Make the provider bank specific. Got to have the same bank id either
#       in the destination or the source.


class TransactionProvider(BaseProvider):
    @staticmethod
    def bank_id():
        return xeger(r"[0-9A-F]{4}")

    def _gen_agnostic_data(self):
        internal_faker = Faker()
        date = internal_faker.iso8601()
        amount = str(abs(internal_faker.pyfloat()))
        currency = internal_faker.currency_code()
        category = internal_faker.name().split(' ')[0]
        return date, amount, currency, category

    def _gen_transaction(self, bankid, incoming=True, outgoing=False):
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

    def transaction(self, bankid):
        date, amount, currency, category = self._gen_agnostic_data()

        # Randomly choose the type of the transaction
        transaction_id, source_id, dest_id =\
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

        return date, transaction_id, source_id,\
               dest_id, amount, currency, category


    def random_transaction(self):
        rule_gen_id = r'^[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-' \
                            r'[0-9A-F]{4}-[0-9A-F]{12}$'
        transaction_id = xeger(rule_gen_id)
        source_id = xeger(rule_gen_id)
        dest_id = xeger(rule_gen_id)
        date, amount, currency, category = self._gen_agnostic_data()
        return date, transaction_id, source_id, dest_id, \
               amount, currency,  category


def generate_multiple_transactions(nr_entries):
    transaction_faker = Faker()
    transaction_faker.add_provider(TransactionProvider)
    bid = transaction_faker.bank_id()
    return [",".join(transaction_faker.transaction(bid)) + "\n"
            for n in range(0, nr_entries)], bid


def generate_fake_transaction_log(filename=None, nr_entries=10):
    transaction_str, bank_id = \
        generate_multiple_transactions(nr_entries)
    if filename is None:
        # Generate with the bank as the filename
        filename = str(bank_id) + ".txt"
    with open(filename, "w") as f:
        f.writelines(transaction_str)

def generate_fake_transaction_log2(filename=None, nr_entries=10):
    transaction_faker = Faker()
    transaction_faker.add_provider(TransactionProvider)
    bank_id = transaction_faker.bank_id()
    transaction_data = [transaction_faker.transaction(bank_id)
            for n in range(0, nr_entries)]
    if filename is None:
        # Generate with the bank as the filename
        filename = str(bank_id) + ".txt"
    with open(filename, 'w') as f:
        writer = csv.writer(f)
        writer.writerows(transaction_data)


if __name__ == "__main__":
    import time

    start = time.time()
    [generate_fake_transaction_log() for x in range(0, 5)]
    duration = (time.time() - start)
    print(duration)
    import time

    start = time.time()
    [generate_fake_transaction_log2() for x in range(0, 5)]
    duration = (time.time() - start)
    print(duration)

    import time

    start = time.time()
    [generate_fake_transaction_log() for x in range(0, 5)]
    duration = (time.time() - start)
    print(duration)

    import time

    start = time.time()
    [generate_fake_transaction_log2() for x in range(0, 5)]
    duration = (time.time() - start)
    print(duration)

    import time
    start = time.time()
    [generate_fake_transaction_log() for x in range(0, 5)]
    duration = (time.time() - start)
    print (duration)
    import time

    start = time.time()
    [generate_fake_transaction_log2() for x in range(0, 5)]
    duration = (time.time() - start)
    print(duration)

    import time

    start = time.time()
    [generate_fake_transaction_log() for x in range(0, 5)]
    duration = (time.time() - start)
    print(duration)

    import time

    start = time.time()
    [generate_fake_transaction_log2() for x in range(0, 5)]
    duration = (time.time() - start)
    print(duration)

    import time
    start = time.time()
    [generate_fake_transaction_log() for x in range(0, 5)]
    duration = (time.time() - start)
    print (duration)
    import time

    start = time.time()
    [generate_fake_transaction_log2() for x in range(0, 5)]
    duration = (time.time() - start)
    print(duration)

    import time

    start = time.time()
    [generate_fake_transaction_log() for x in range(0, 5)]
    duration = (time.time() - start)
    print(duration)

    import time

    start = time.time()
    [generate_fake_transaction_log2() for x in range(0, 5)]
    duration = (time.time() - start)
    print(duration)

    import time
    start = time.time()
    [generate_fake_transaction_log() for x in range(0, 5)]
    duration = (time.time() - start)
    print (duration)
    import time

    start = time.time()
    [generate_fake_transaction_log2() for x in range(0, 5)]
    duration = (time.time() - start)
    print(duration)

    import time

    start = time.time()
    [generate_fake_transaction_log() for x in range(0, 5)]
    duration = (time.time() - start)
    print(duration)

    import time

    start = time.time()
    [generate_fake_transaction_log2() for x in range(0, 5)]
    duration = (time.time() - start)
    print(duration)