import csv
from datetime import datetime
import os
import time
import requests
import logging

from sqlalchemy import delete, extract, func
from sqlalchemy.exc import IntegrityError

from app.db import db
from consts.consts import (
    GENERATE_REPORT_URL,
    REQUEST_HEADERS,
    RETRIEVE_ACCOUNT_SUMMARY_URL,
    RETRIEVE_OPEN_POSITIONS_URL,
    RETRIEVE_REPORT_URL,
)
from models.models import AccountMetadata, Company, Dividend, DividendReport, YearlyDividends
from models.classes import AccountSummaryResponse, DividendHistory
from utils.endpoint_utils import end_of_or_today


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
    """Fetch and update the Account Summary in the database"""

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


def sync_dividend_history(year: int):
    """Request Trading 212 to make a new Report and Download it"""

    logger.info(f"Starting dividend history download for year {year}")

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
        logger.error(
            f"Unable to request report from Trading212 for {year}: {response.json()}"
        )

    reportId = response.json().get("reportId")

    # Allow Trading 212 to process the request
    # Can't use a loop here to continue pinging T212 due to rate limiting
    time.sleep(20)

    # Download report from Trading 212 using above response ID
    response = requests.get(RETRIEVE_REPORT_URL, headers=REQUEST_HEADERS)
    if response.status_code != 200:
        logger.error(
            f"Report for {year} requested successfully, though retrevial from Trading212 has failed: {response.json()}"
        )

    # Iterate through response to find correct report
    for item in response.json():
        if item["reportId"] == int(reportId):
            dividend_history = DividendHistory(
                reportId=item["reportId"],
                downloadLink=item["downloadLink"],
                timeFrom=item["timeFrom"],
                timeTo=item["timeTo"],
            )

            r = requests.get(item["downloadLink"], stream=True)
            r.raise_for_status()
            with open("downloaded.csv", "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            if report := (
                db.session.query(DividendReport)
                .filter(extract("year", DividendReport.time_from) == year)
                .one_or_none()
            ):
                db.session.delete(report)
                stmt = delete(Dividend).where(Dividend.year == year)
                db.session.execute(stmt)
                stmt = delete(YearlyDividends).where(YearlyDividends.year == year)
                db.session.execute(stmt)
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

            with open("downloaded.csv", "r") as file:
                reader = csv.DictReader(file)
                total_count: float = 0.0
                for row in reader:
                    total_count += float(row["Total"])
                    db.session.add(
                        Dividend(
                            report_id=dividend_history.reportId,
                            ticker=row["Ticker"],
                            payment_date=datetime.fromisoformat(row["Time"]),
                            year=datetime.fromisoformat(row["Time"]).year,
                            total_payment=row["Total"],
                            number_of_shares=row["No. of shares"],
                            currency=row["Currency (Price / share)"],
                        )
                    )

                db.session.add(
                    YearlyDividends(
                        year=year,
                        total_dividends=total_count,
                    )
                )
                db.session.commit()

            os.remove("downloaded.csv")

