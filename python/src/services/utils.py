import csv
from datetime import datetime
from decimal import Decimal

from app.db import db
from models.models import Company, Dividend, YearlyDividends


def calculate_estimated_deposits(
    total_cost: float, total_dividends: float, realised_profit_loss: float
) -> Decimal:
    return Decimal(str(total_cost - total_dividends - realised_profit_loss))


def process_dividend_csv(file_path: str, report_id: int, year: int) -> None:
    placeholder_company = (
        db.session.query(Company).filter(Company.ticker == "UNKNOWN").one()
    )

    with open(file_path, "r") as file:
        reader = csv.DictReader(file)
        total_count: float = 0.0
        for row in reader:
            company = (
                db.session.query(Company)
                .filter(Company.name == row["Name"])
                .one_or_none()
            )
            total_count += float(row["Total"])
            db.session.add(
                Dividend(
                    report_id=report_id,
                    company_id=company.id if company else placeholder_company.id,
                    payment_date=datetime.fromisoformat(row["Time"]),
                    year=datetime.fromisoformat(row["Time"]).year,
                    total_payment=row["Total"],
                    number_of_shares=row["No. of shares"],
                    currency=row["Currency (Price / share)"],
                )
            )

        previous_year_count = (
            db.session.query(YearlyDividends.total_dividends)
            .filter(YearlyDividends.year == year - 1)
            .one_or_none()
        )
        percentage_increase: float = 0.0

        if previous_year_count and float(previous_year_count.total_dividends) > 0:
            previous_total = float(previous_year_count.total_dividends)
            percentage_increase = (
                (total_count - previous_total) / previous_total
            ) * 100

        db.session.add(
            YearlyDividends(
                year=year,
                total_dividends=total_count,
                yoy_increase=percentage_increase,
            )
        )
        db.session.commit()
