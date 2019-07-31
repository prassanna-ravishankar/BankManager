import argparse
import csv
import json
import os
from bank import Bank
from transaction import TransactionList
from money import xrates

# Exchange rate faker
xrates.install('money.exchange.SimpleBackend')
xrates.base = 'USD'  # All base currency is in USD.


def parse_currency_file(folder_data):
    # Load currency exchange before anything else
    currency_rates = json.load(open(os.path.join(folder_data,
                                                 "currency_rates.json"), "r"))
    for currency, currency_rate in currency_rates.items():
        xrates.setrate(currency, currency_rate)


def parse_log_file(filename, bank_transaction_list):
    with open(filename, "r") as f:
        reader = csv.reader(f)
        for transaction in reader:
            date, transaction_id, source_id, dest_id, \
            amount, currency, category = transaction

            bank_transaction_list.add_transaction(
                date, source_id, dest_id, transaction_id,
                amount, currency, category
            )


def parse_transaction_file(folder_transaction):
    filename = os.path.join(folder_transaction, "transactions.csv")
    transaction_lists = dict()
    with open(filename, "r") as f:
        reader = csv.reader(f)
        for entry in reader:
            date, bank_code, bank_tz, transaction_file, bank_name = entry
            current_bank = Bank(bank_code,
                                bank_tz,
                                bank_name)
            if bank_code not in transaction_lists.keys():
                transaction_lists[bank_code] = TransactionList(current_bank)
            print(bank_name, bank_code)
            parse_log_file(
                os.path.join(folder_transaction, transaction_file),
                transaction_lists[bank_code]
            )
            # print(date, bank_code, bank_tz, transaction_file, bank_name)
            print(transaction_lists[bank_code].currencies())
    return transaction_lists


def categorize_transactions_for_bank(bankid, all_transactions):
    assert bankid in all_transactions, "Didn't parse transactions for this bank"
    my_categorized_transaction = all_transactions[bankid].categorize()
    return my_categorized_transaction


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--transaction_folder", type=str,
                        help="What is the transaction folder",
                        default="./transactions")
    parser.add_argument("-r", "--result_folder", type=str,
                        default="./results",
                        help="What is the results folder")
    args = parser.parse_args()
    parse_currency_file(os.path.abspath(args.transaction_folder))
    all_transaction_lists = \
        parse_transaction_file(os.path.abspath(args.transaction_folder))
    categorized_bank_transactions = categorize_transactions_for_bank(
        list(all_transaction_lists.keys())[0],
        all_transaction_lists
    )
    print (categorized_bank_transactions)
    pass