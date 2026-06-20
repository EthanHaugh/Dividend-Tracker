from datetime import datetime, timedelta
from decimal import Decimal
import os
import requests
import logging

from sqlalchemy import delete, extract, func
from sqlalchemy.exc import IntegrityError
from celery_service.services.utils import (
    process_dividend_csv,
)

from database.db import db
from consts.consts import (
    GENERATE_REPORT_URL,
    REQUEST_HEADERS,
    RETRIEVE_ACCOUNT_SUMMARY_URL,
    RETRIEVE_ACCOUNT_TRANSACTIONS_URL,
    RETRIEVE_OPEN_POSITIONS_URL,
    RETRIEVE_REPORT_URL,
)
from database.models import (
    AccountMetadata,
    AccountTransactions,
    Company,
    Dividend,
    DividendReport,
    TransactionType,
    YearlyDividends,
)
from models.classes import AccountSummaryResponse, DividendHistory
from utils.endpoint_utils import end_of_or_today


logger = logging.getLogger(__name__)

""" 
Celery Tasks to fetch and update the DB 

For more information on the Trading 212 API see
https://docs.trading212.com/api
"""


def sync_open_positions() -> None:
    """Fetch and update open positions in the database"""

    response = requests.get(RETRIEVE_OPEN_POSITIONS_URL, headers=REQUEST_HEADERS)
    if response.status_code != 200:
        raise RuntimeError(
            f"Unable to retrieve open positions from Trading212: {response.json()}"
        )

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
                    name=company["instrument"]["name"],
                    quantity=company["quantity"],
                    initial_buy_date=datetime.fromisoformat(company["createdAt"]),
                    average_buy_price=float(company["averagePricePaid"]),
                )
            )
    db.session.commit()

    # For historical data, carry out no clean up on no longer open poisitons
    # Maybe add a new row in the Company table to indicate if a position is open/close?


def sync_account_summary() -> None:
    """Fetch and update the Account Summary in the database"""

    response = requests.get(RETRIEVE_ACCOUNT_SUMMARY_URL, headers=REQUEST_HEADERS)
    if response.status_code != 200:
        raise RuntimeError(
            f"Unable to retrieve account summary from Trading212: {response.json()}"
        )

    response_data = AccountSummaryResponse(**response.json())

    account_metadata = db.session.query(AccountMetadata).first()
    estimated_deposits = (
        db.session.query(
            func.coalesce(func.sum(AccountTransactions.transaction_amount), 0)
        )
        .filter(AccountTransactions.transaction_type != TransactionType.FEE)
        .scalar()
    )
    one_year_ago = datetime.now() - timedelta(days=365)
    estimated_yearly_contribution = (
        db.session.query(
            func.coalesce(func.sum(AccountTransactions.transaction_amount), 0)
        )
        .filter(AccountTransactions.transaction_type != TransactionType.FEE)
        .filter(AccountTransactions.transaction_date >= one_year_ago)
        .scalar()
    )

    current_value = Decimal(str(response_data.investments.currentValue))

    if not account_metadata:
        account_metadata = AccountMetadata(
            account_value=current_value,
            estimated_deposits=estimated_deposits,
            estimated_contribution_year=estimated_yearly_contribution,
        )
        db.session.add(account_metadata)
    else:
        account_metadata.account_value = current_value
        account_metadata.estimated_deposits = estimated_deposits
        account_metadata.estimated_contribution_year = estimated_yearly_contribution

    db.session.commit()


def request_dividend_report(year: int) -> int:
    """
    POST to Trading 212 to generate a dividend report.
    Returns the reportId for the follow-up download task.
    """
    payload = {
        "dataIncluded": {
            "includeDividends": True,
            "includeInterest": False,
            "includeOrders": False,
            "includeTransactions": False,
        },
        "timeFrom": f"{year}-01-01T00:00:00Z",
        "timeTo": f"{end_of_or_today(year)}T00:00:00Z",
    }

    response = requests.post(GENERATE_REPORT_URL, headers=REQUEST_HEADERS, json=payload)
    if response.status_code != 200:
        raise RuntimeError(
            f"Failed to request Trading 212 report for {year}: {response.json()}"
        )

    report_id = response.json().get("reportId")
    if not report_id:
        raise ValueError(f"Trading 212 response missing reportId for year {year}")

    logger.info(f"Report requested successfully for {year}, reportId={report_id}")
    return int(report_id)


def download_and_process_report(report_id: int, year: int) -> None:
    """
    Retrieve the completed report from Trading 212, download the CSV,
    persist it to the database, then clean up.
    """
    response = requests.get(RETRIEVE_REPORT_URL, headers=REQUEST_HEADERS)
    if response.status_code != 200:
        raise RuntimeError(
            f"Failed to retrieve report list from Trading 212: {response.json()}"
        )

    # Find the matching report in the response list
    dividend_history: DividendHistory | None = None
    for item in response.json():
        if item["reportId"] == report_id:
            dividend_history = DividendHistory(
                reportId=item["reportId"],
                downloadLink=item["downloadLink"],
                timeFrom=item["timeFrom"],
                timeTo=item["timeTo"],
            )
            break

    if dividend_history is None:
        raise ValueError(
            f"Report {report_id} not found in Trading 212 report list — "
            "it may still be processing. Consider retrying."
        )

    # Download the CSV
    csv_response = requests.get(dividend_history.downloadLink, stream=True)
    csv_response.raise_for_status()

    tmp_path = f"dividend_{report_id}_{year}.csv"
    with open(tmp_path, "wb") as f:
        f.write(csv_response.content)

    # Clear out any existing data for this year before re-inserting
    if existing_report := (
        db.session.query(DividendReport)
        .filter(extract("year", DividendReport.time_from) == year)
        .one_or_none()
    ):
        db.session.delete(existing_report)
        db.session.execute(delete(Dividend).where(Dividend.year == year))
        db.session.execute(delete(YearlyDividends).where(YearlyDividends.year == year))
        db.session.commit()

    try:
        db.session.add(
            DividendReport(
                report_id=dividend_history.reportId,
                time_from=datetime.fromisoformat(dividend_history.timeFrom),
                time_to=datetime.fromisoformat(dividend_history.timeTo),
                created_at=datetime.now(),
            )
        )
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        logger.warning(f"DividendReport {report_id} already exists — skipping insert.")

    try:
        process_dividend_csv(tmp_path, dividend_history.reportId, year)
    finally:
        os.remove(tmp_path)


def sync_company_dividends() -> None:
    """Check that the Company totals match whats in the Dividends table"""
    companies = db.session.query(Company).all()

    for company in companies:
        total_payments = (
            db.session.query(func.sum(Dividend.total_payment).label("total_payment"))
            .where(Dividend.company_id == company.id)
            .scalar()
        )

        company.total_payments = total_payments or Decimal(0)

    db.session.commit()


def sync_account_transactions() -> None:
    """Update the Account Transactions table"""

    def processItems(data: dict):
        if (items := data.get("items")) is not None:
            for item in items:
                try:
                    db.session.add(
                        AccountTransactions(
                            id=item["reference"],
                            transaction_date=datetime.fromisoformat(
                                item["dateTime"].replace("Z", "+00:00")
                            ),
                            created_at=datetime.now(),
                            updated_at=datetime.now(),
                            transaction_amount=item["amount"],
                            transaction_type=TransactionType[item["type"]],
                        )
                    )
                    db.session.commit()
                except IntegrityError:
                    # Using the item.reference as the primary key, ensure it
                    # isn't already in the db, otherwise rollback and drop out
                    # since we've already logged these transactions
                    db.session.rollback()
                    logger.info("Duplicate Transaction Found...")

    response = requests.get(RETRIEVE_ACCOUNT_TRANSACTIONS_URL, headers=REQUEST_HEADERS)
    data = response.json()
    processItems(data)

    while data.get("nextPagePath") is not None:
        response = requests.get(
            f"{RETRIEVE_ACCOUNT_TRANSACTIONS_URL}&{data.get('nextPagePath').removeprefix('limit=50')}",
            headers=REQUEST_HEADERS,
        )

        data = response.json()

        processItems(data)

    # Capture first deposit date
    initial_deposit_date: datetime = datetime.fromisoformat(
        data["items"][-1]["dateTime"].replace("Z", "+00:00")
    )

    metadata = db.session.query(AccountMetadata).first()

    if metadata:
        metadata.initial_deposit_date = initial_deposit_date
        db.session.commit()
