# BankManager
This project describes BankManager, which is a possible solution to the coding challenge.

## Introduction
This project consists of multiple components. It has a base module called bankmanager (lower case) which actually defines the different components. These can be looked at to understand the internal structure - otherwise they are pretty much useless. In addition, there are two entry level files (which you will execute) : a) generate_transactions.py and b)parse_transactions.py.

Some basic description :-
- `generate_transactions.py` - is a fake data generator
- `parse_transactions.py` - this parses the transactions 
- `config.py` - These contains constants regarding BANK ID formats, Bank Account formats, and the global base currency (could be adapted to a bank-wise base currency)

__Currency Rates__ : The coding challenge stays quiet regarding different currencies (in order to calculate the balances). I have added the necessity to have a currency conversion data, and all balances are returned in BASE_CURRENCY (USD by default. Can change in `config.py`). The transaction faker `generate_transactions.py` fakes timestamped currency conversion related information as well and saves them to `currency_rates.json` in the transaction folder by default. This parameter can be controlled. I have attached a `sample_currency_rates.json` in order to understand the format of this file. You have to pass a currency_rates.json; otherwise unexpected calculations might occur (might assume all currencies to have a ratio of 1 with USD).

As for the code in the module, since it is python, a lot of it is self explanatory. I have provided descriptions wherever necessary. There are cases where I am doing something strange or unique , and those cases are commented 

There is also a CHANGELOG were you can see the commit history pushed to my private repository. If required, I can give you access to the github repository : `https://github.com/atemysemicolon/BankManager` which is currently private


## Requirements and Installing
- *OS*
    + This has been developed and tested on a Ubuntu 18.10 (and 19.04 running from windows using WSL)
    + This in principle should work on MAC as well
    + This would work on windows as well, but the instructions would be different
- *Python version*
    + This has been tested on Python 3.6.5
    + It should work in principle above python 3.2 
- *Python requirements*
    + You might need something like virtualenv or pyenv (with the virtualenv plugin) or pipenv to test this in an isolated fashion
    + It was developed using pyenv and pyenv-virtualenv to maintain an isolated environment.
    + Otherwise, when you install the requirements for this, it will pollute your system's environment
    + You can install pipenv(for example with) `pip install pipenv`
- *Environment Setup*
    + Activate your virtual environment (if you are using pyenv or virtualenv)
        * Usually `source <path-of-virtualenv>/activate.sh`
    + Skip this step if you are using your global python version, or if you are using pipenv
- *Download this and extract this folder* to some <project-root>
- *Installing Requirements*
    + Navigate to <project-root>
    + if you are using pipenv, you can setup the requirements as `pipenv install -r requirements.txt` or just `pipenv install`.
    + Alternatively, if you have activated a virtualenv, or you're planning to pollute your global python environment, do `pip install -r requirements.txt`


## Usage

### 1. Fake Transaction Generator
- Execute `./generate_transactions.py`
- Execute `./generate_transactions.py --help` for the following help
```
Usage: generate_transactions.py [-h] [-t TRANSACTION_FOLDER]
                                [-c CURRENCY_RATES] [-b BANKS] [-e ENTRIES]
                                [-l LOGSIZE]

Generate fake bank data with currency rates too

optional arguments:
  -h, --help            show this help message and exit
  -t TRANSACTION_FOLDER, --transaction_folder TRANSACTION_FOLDER
                        What is the transaction folder
  -c CURRENCY_RATES, --currency_rates CURRENCY_RATES
                        The name of the currency rates file
  -b BANKS, --banks BANKS
                        Number of banks
  -e ENTRIES, --entries ENTRIES
                        Number of logs per bank
  -l LOGSIZE, --logsize LOGSIZE
                        Number of transactions per log
```
- This can be used without any parameter - the defaults are good enough
- This would generate data for some fake banks
- It uses Faker, heavily. 
- This acts as an end to end test (generation + parsing should not fail)
- It generates also a date-dependent currency conversion chart

### 2. Parse Fake or Real Data.
- Execute `./parse_transactions.py`
- Execute `./parse_transactions.py --help` for the following help
```
usage: Transaction parser.Works with fake data or real dataNot tested when currency rates are not passed
       [-h] [-t TRANSACTION_FOLDER] [-r RESULT_FOLDER] [-c CURRENCY_RATES]

optional arguments:
  -h, --help            show this help message and exit
  -t TRANSACTION_FOLDER, --transaction_folder TRANSACTION_FOLDER
                        What is the transaction folder
  -r RESULT_FOLDER, --result_folder RESULT_FOLDER
                        What is the results folder
  -c CURRENCY_RATES, --currency_rates CURRENCY_RATES
                        The name of the currency rates file. This path is
                        relative to current folder, and *not* relative to
                        transaction folder
```
- This is self explanatory
- Default params work as described in the problem statement
- Added a little bit of loop visualization using tqdm


### 3. Test different components (Integrity test)
- From the project root (not from inside the folder `tests`) execute `pytest`
- No parameters need to be passed
- You can also do tests matching an expression with `pytest -k"expression"`
- Look at `tests/test_bank.py` to see all the tests (all tests using the naming  test_xxx).

## Future Work
1. Use something like SQL alchemy to automate the backend.
2. Use more parellel processing
3. Look at my other project https://github.com/atemysemicolon/Blockchain-Course-101/tree/master/LiveCoding 
    - It is *very very easy* to convert this into a blockchain
4. A way to test fails in regex better.
5. Make a gui to make this even better