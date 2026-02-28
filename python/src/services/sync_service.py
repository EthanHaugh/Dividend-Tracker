from datetime import datetime
import requests
import logging

from sqlalchemy import func

from app.db import db
from consts.consts import REQUEST_HEADERS, RETRIEVE_ACCOUNT_SUMMARY_URL, RETRIEVE_OPEN_POSITIONS_URL
from models.models import AccountMetadata, Company, YearlyDividends
from models.classes import AccountSummaryResponse


logger = logging.getLogger(__name__)


def sync_open_positions() -> None:
    """Fetch and update open positions in the database"""

    logger.info("Starting sync_positions_task")

    response = requests.get(RETRIEVE_OPEN_POSITIONS_URL, headers=REQUEST_HEADERS)
    if response.status_code != 200:
        logger.error(
            f"Unable to retrieve open positions from Trading212: {response.json()}"
        )
        return

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

def sync_account_summary() -> None:
    response = requests.get(RETRIEVE_ACCOUNT_SUMMARY_URL, headers=REQUEST_HEADERS)
    if response.status_code != 200:
        logger.error(
            f"Unable to retrieve account summary from Trading212: {response.json()}"
        )
        return
    
    response_data = AccountSummaryResponse(**response.json())

    total_dividends: float = float(
        db.session.query(func.sum(YearlyDividends.total_dividends)).scalar()
    )
    account_metadata = db.session.query(AccountMetadata).first()
    estimated_deposits = (
        response_data.investments.totalCost
        - total_dividends
        - response_data.investments.realizedProfitLoss
    )
    current_value = response_data.investments.currentValue

    if not account_metadata:
        account_metadata = AccountMetadata(
            account_value=current_value, estimated_deposits=estimated_deposits
        )
        db.session.add(account_metadata)
    else:
        account_metadata.account_value = current_value
        account_metadata.estimated_deposits = estimated_deposits

    db.session.commit()

