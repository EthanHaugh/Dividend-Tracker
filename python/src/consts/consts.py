import os

API_KEY = os.getenv("TRADING212KEY")

GENERATE_REPORT_URL = "https://live.trading212.com/api/v0/history/exports"

RETRIEVE_REPORT_URL = "https://live.trading212.com/api/v0/history/exports"

RETRIEVE_OPEN_POSITIONS_URL = "https://live.trading212.com/api/v0/equity/portfolio"

REQUEST_HEADERS = {"Authorization": API_KEY}
