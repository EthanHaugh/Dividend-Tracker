import os


API_KEY = os.getenv("TRADING212KEYID")

API_KEY_SECRET = os.getenv("TRADING212KEY")

GENERATE_REPORT_URL = "https://live.trading212.com/api/v0/equity/history/exports"

RETRIEVE_REPORT_URL = "https://live.trading212.com/api/v0/history/exports"

RETRIEVE_OPEN_POSITIONS_URL = "https://live.trading212.com/api/v0/equity/portfolio"

RETRIEVE_ACCOUNT_CASH_URL = "https://live.trading212.com/api/v0/equity/account/cash"

REQUEST_HEADERS = {"Authorization": API_KEY_SECRET}
