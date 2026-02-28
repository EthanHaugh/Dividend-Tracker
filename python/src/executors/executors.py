import csv
import os
from datetime import datetime

from sqlalchemy import extract, delete, func
from models.classes import AccountSummaryResponse, DividendHistory
from sqlalchemy.exc import IntegrityError
from app.db import db

from models.models import (
    AccountMetadata,
    Dividend,
    DividendReport,
    YearlyDividends,
)


def process_report(response_data: DividendHistory, year: int) -> None:
    # Look for existing report with specified year, if one exists delete it
    # and update the table with up to date report
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
                report_id=response_data.reportId,
                time_from=datetime.fromisoformat(response_data.timeFrom),
                time_to=datetime.fromisoformat(response_data.timeTo),
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
                    report_id=response_data.reportId,
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


def update_account(response_data: AccountSummaryResponse) -> None:
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
