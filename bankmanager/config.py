"""
Global config params.
Edit this only if you want to change things like base currency,  etc.
"""

BASE_CURRENCY = "USD"  # Base currency to calculate the sum
BANK_ID_RULE = r"[0-9A-F]{4}$"
BANK_ACCOUNT_RULE = r'^[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-' \
                    r'[0-9A-F]{4}-[0-9A-F]{12}$'
BANKLESS_ACCOUNT_RULE = r'^[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-' \
                        r'[0-9A-F]{4}-[0-9A-F]{12}$'

