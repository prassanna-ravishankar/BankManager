#!/usr/bin/env python3
"""
This is the source code of the parser.
It acts like the "main" for the rest of the code.
It populates entities of the module bankmanager, and uses that to
make some calculations

Hover down to the if __name__ == "__main__" to understand parameters
"""
import argparse
import csv
import os
import logging
from tqdm import tqdm  # Progress bar coz why not
from bankmanager.bank import Bank
from bankmanager.transaction import TransactionList
from bankmanager.currencyrates import CurrencyRateList
from bankmanager import config

logger = logging.getLogger("Transaction Parser")


def parse_log_file(filename, bank_transaction_list):
    with open(filename, "r") as f:
        logging.info("Parsing log file : " + filename)
        reader = csv.reader(f)
        for transaction in reader:
            date, transaction_id, source_id, \
            dest_id, amount, currency, category = transaction

            bank_transaction_list.add_transaction(
                date, source_id, dest_id, transaction_id,
                amount, currency, category
            )


def parse_transaction_file(folder_transaction, currency_rates):
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
                transaction_lists[bank_code] = TransactionList(current_bank,
                                                               currency_rates)
            parse_log_file(
                os.path.join(folder_transaction, transaction_file),
                transaction_lists[bank_code]
            )
    logger.info("Parsed Transactions in " + filename)
    return transaction_lists


def write_bank_details(transaction_lists, filename):
    things_to_write = {}
    for bank_code, transaction_list in transaction_lists.items():
        things_to_write[bank_code] = transaction_list.bank.name
    with open(filename, 'w') as f:
        writer = csv.writer(f)
        for bank_code in sorted(things_to_write.keys()):
            writer.writerow((bank_code, things_to_write[bank_code]))
    logger.info("Written Banks.csv with bank_code")
    pass


def categorize_transactions_for_bank(bankid, all_transactions):
    assert bankid in all_transactions, "Didn't parse transactions for this bank"
    my_categorized_transactions = TransactionList.categorize(
        all_transactions[bankid]
    )
    return my_categorized_transactions


def categorize_transactions_for_bank_by_date(bankid, all_transactions):
    assert bankid in all_transactions, "Didn't parse transactions for this bank"
    my_categorized_transactions = TransactionList.categorize_by_date(
        all_transactions[bankid]
    )
    return my_categorized_transactions


def write_daily_balances(bankid, categorized_date_transactions, result_folder,
                         filename_prefix="_daily_balances.csv"):
    data_to_write  = []
    for date in categorized_date_transactions.keys():
        outgoing_amount, incoming_amount, _ = \
            categorized_date_transactions[date].calculate_balance()
        data_to_write.append(
            (date,
             outgoing_amount[0],
             outgoing_amount[1],
             incoming_amount[0],
             incoming_amount[1]
             )
        )

    with open(os.path.join(result_folder, bankid + filename_prefix), "w") as f:
        writer = csv.writer(f)
        # base currency is the same so not sorting it w.r.t to that
        for data in sorted(data_to_write, key=lambda x: x[0]):
            writer.writerow((data[0], config.BASE_CURRENCY,
                             data[1], data[2], data[3], data[4]))
    logger.info(
        "Written {}.csv with daily balances".format(bankid + filename_prefix)
    )


def write_category_balances(bankid, categorized_categorical_transactions,
                            result_folder,
                            filename_prefix="_categories.csv"):
    data_to_write  = []
    for category in categorized_categorical_transactions.keys():
        outgoing_amount, incoming_amount, internal_count = \
            categorized_categorical_transactions[category].calculate_balance()
        data_to_write.append(
            (category,

             # Determins amount in config.BASE_CURRENCY
             categorized_categorical_transactions[category].balance,

             # Outgoing + Incoming + Internal Count
             outgoing_amount[1] + incoming_amount[1] + internal_count,
             )
        )

    with open(os.path.join(result_folder, bankid + filename_prefix), "w") as f:
        writer = csv.writer(f)
        # base currency is the same so not sorting it w.r.t to that
        for cat, amount, txcount in sorted(data_to_write, key=lambda x: x[0]):
            writer.writerow(
                (
                    cat,
                    config.BASE_CURRENCY,
                    amount,
                    txcount
                )
            )
    logger.info("Written {}.csv with category based split balances, for "
                "bank_name".format(bankid + filename_prefix))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser("Transaction parser."
                                     "Works with fake data or real data"
                                     "Not tested when currency rates are not passed")
    parser.add_argument("-t", "--transaction_folder", type=str,
                        help="What is the transaction folder",
                        default="./transactions")
    parser.add_argument("-r", "--result_folder", type=str,
                        default="./results",
                        help="What is the results folder")
    parser.add_argument("-c", "--currency_rates", type=str,
                        default=None,
                        help="The name of the currency rates file. This path "
                             "is relative to current folder, and *not* "
                             "relative to transaction folder")
    args = parser.parse_args()

    result_folder = os.path.abspath(args.result_folder)

    # Make Result folder if it does not exist
    if not os.path.exists(result_folder):
        os.mkdir(result_folder)

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
        parse_transaction_file(os.path.abspath(args.transaction_folder),
                               currency_list)

    logger.info("Writing Bank details to banks.csv")
    write_bank_details(
        all_transaction_lists,
        os.path.join(result_folder, "banks.csv")
    )

    logger.info("Processing daily and categorical balances")
    for bank_id in tqdm(list(all_transaction_lists.keys())):
        logger.info("On bank id: " + bank_id)
        categorized_bank_transactions = categorize_transactions_for_bank_by_date(
            bank_id,
            all_transaction_lists,
        )
        write_daily_balances(bank_id,
                             categorized_bank_transactions,
                             result_folder)
        categorized_bank_transactions = categorize_transactions_for_bank(
            bank_id,
            all_transaction_lists,
        )
        write_category_balances(bank_id,
                                categorized_bank_transactions,
                                result_folder)
    pass