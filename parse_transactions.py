import argparse
import csv
import json
import os
from bank import Bank
from transaction import TransactionList
from currencyrates import CurrencyRateList


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
    parser.add_argument("-c", "--currency_rates", type=str,
                        default=None,
                        help="The name of the currency rates file")
    args = parser.parse_args()

    if not args.currency_rates:
        filename_currency = os.path.join(
            os.path.abspath(args.transaction_folder),
            "currency_rates.json"
        )
    else:
        filename_currency = args.currency_rates
    currency_list = CurrencyRateList.load(
        filename_currency
    )
    all_transaction_lists = \
        parse_transaction_file(os.path.abspath(args.transaction_folder))

    print ( "Random bank balance : ", all_transaction_lists[list(all_transaction_lists.keys())[9]].calculate_balance(currency_list))
    categorized_bank_transactions = categorize_transactions_for_bank(
        list(all_transaction_lists.keys())[0],
        all_transaction_lists
    )
    print (categorized_bank_transactions)
    pass