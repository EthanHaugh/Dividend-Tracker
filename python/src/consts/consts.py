import base64
import os

API_KEY_ID = os.getenv("TRADING212KEYID")

API_KEY_SECRET = os.getenv("TRADING212KEY")

API_KEY = base64.b64encode(f"{API_KEY_ID}:{API_KEY_SECRET}".encode('utf-8')).decode('utf-8')

GENERATE_REPORT_URL = "https://live.trading212.com/api/v0/equity/history/exports"

RETRIEVE_REPORT_URL = "https://live.trading212.com/api/v0/history/exports"

RETRIEVE_OPEN_POSITIONS_URL = "https://live.trading212.com/api/v0/equity/positions"

RETRIEVE_ACCOUNT_SUMMARY_URL = "https://live.trading212.com/api/v0/equity/account/summary"

REQUEST_HEADERS = {"Authorization": f"Basic {API_KEY}"}
