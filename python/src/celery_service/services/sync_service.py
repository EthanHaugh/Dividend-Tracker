from datetime import datetime
from decimal import Decimal
import os
import requests
import logging

from sqlalchemy import delete, extract, func
from sqlalchemy.exc import IntegrityError
from celery_service.services.utils import (
    calculate_estimated_deposits,
    process_dividend_csv,
)

from database.db import db
from consts.consts import (
    GENERATE_REPORT_URL,
    REQUEST_HEADERS,
    RETRIEVE_ACCOUNT_SUMMARY_URL,
    RETRIEVE_OPEN_POSITIONS_URL,
    RETRIEVE_REPORT_URL,
)
from database.models import (
    AccountMetadata,
    Company,
    Dividend,
    DividendReport,
    YearlyDividends,
)
from routes.classes import AccountSummaryResponse, DividendHistory
from routes.endpoint_utils import end_of_or_today


logger = logging.getLogger(__name__)

""" 
Celery Tasks to fetch and update the DB 

For more information on the Trading 212 API see
https://docs.trading212.com/api
"""


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
                    name=company["instrument"]["name"],
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
    """Fetch and update the Account Summary in the database"""

    response = requests.get(RETRIEVE_ACCOUNT_SUMMARY_URL, headers=REQUEST_HEADERS)
    if response.status_code != 200:
        logger.error(
            f"Unable to retrieve account summary from Trading212: {response.json()}"
        )
        return

    response_data = AccountSummaryResponse(**response.json())

    # Yearly Dividends may be empty if no reports have been downloaded
    total_dividends: float = float(
        db.session.query(func.sum(YearlyDividends.total_dividends)).scalar() or 0.0
    )

    account_metadata = db.session.query(AccountMetadata).first()
    estimated_deposits = calculate_estimated_deposits(
        response_data.investments.totalCost,
        total_dividends,
        response_data.investments.realizedProfitLoss,
    )
    current_value = Decimal(str(response_data.investments.currentValue))

    if not account_metadata:
        account_metadata = AccountMetadata(
            account_value=current_value, estimated_deposits=estimated_deposits
        )
        db.session.add(account_metadata)
    else:
        account_metadata.account_value = current_value
        account_metadata.estimated_deposits = estimated_deposits

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
