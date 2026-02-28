from datetime import datetime
import requests
import logging

from app.db import db
from consts.consts import REQUEST_HEADERS, RETRIEVE_OPEN_POSITIONS_URL
from models.models import Company


logger = logging.getLogger(__name__)


def sync_open_positions() -> None:
    """Fetch and update open positions in the database"""

    logger.info("Starting sync_positions_task")

    response = requests.get(RETRIEVE_OPEN_POSITIONS_URL, headers=REQUEST_HEADERS)
    if response.status_code != 200:
        logger.error(
            f"Unable to retrieve open positions from Trading212: {response.json()}"
        )

    logger.info("Processing Companies...")
    for company in response.json():
        # Check for existing company and update
        existing_company: Company | None = (
            db.session.query(Company)
            .filter_by(ticker=company["instrument"]["ticker"])
            .one_or_none()
        )
        if existing_company:
            existing_company.quantity = company["quantity"]
            existing_company.average_buy_price = company["averagePricePaid"]
        else:
            # If no company is found, add a new row
            db.session.add(
                Company(
                    ticker=company["instrument"]["ticker"],
                    quantity=company["quantity"],
                    initial_buy_date=datetime.fromisoformat(company["createdAt"]),
                    average_buy_price=float(company["averagePricePaid"]),
                )
            )
    logger.info("Finished Processing Companies!")
    db.session.commit()

    # For historical data, carry out no clean up on no longer open poisitons
    # Maybe add a new row in the Company table to indicate if a position is open/close?
