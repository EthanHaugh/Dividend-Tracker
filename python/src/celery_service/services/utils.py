import csv
from datetime import datetime
from decimal import Decimal

from database.db import db
from database.models import Company, Dividend, MonthlyDividends, YearlyDividends


def process_dividend_csv(file_path: str, report_id: int, year: int) -> None:
    placeholder_company = (
        db.session.query(Company).filter(Company.ticker == "UNKNOWN").one()
    )

    with open(file_path, "r") as file:
        reader = csv.DictReader(file)
        total_count: float = 0.0
        monthly_totals: dict[tuple[int, int], Decimal] = {}
        for row in reader:
            company = (
                db.session.query(Company)
                .filter(Company.name == row["Name"])
                .one_or_none()
            )

            payment_timestamp = row.get("Time (UTC)") or row.get("Time")
            if not payment_timestamp:
                continue

            payment_datetime = datetime.fromisoformat(payment_timestamp)
            payment_year = payment_datetime.year
            payment_month = payment_datetime.month

            total_amount = Decimal(row["Total"])

            total_count += float(total_amount)
            month_key = (payment_year, payment_month)
            monthly_totals[month_key] = (
                monthly_totals.get(month_key, Decimal("0")) + total_amount
            )

            dividend = Dividend(
                report_id=report_id,
                company_id=company.id if company else placeholder_company.id,
                payment_date=payment_datetime,
                year=payment_year,
                total_payment=total_amount,
                number_of_shares=row["No. of shares"],
                currency=row["Currency (Price / share)"],
            )

            db.session.add(dividend)
            if company:
                company.total_payments += dividend.total_payment
            else:
                placeholder_company.total_payments += dividend.total_payment

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

        for (month_year, month), month_total in monthly_totals.items():
            monthly_dividend = (
                db.session.query(MonthlyDividends)
                .filter(
                    MonthlyDividends.year == month_year,
                    MonthlyDividends.month == month,
                )
                .one_or_none()
            )

            if monthly_dividend:
                monthly_dividend.total_dividends = month_total
            else:
                db.session.add(
                    MonthlyDividends(
                        year=month_year,
                        month=month,
                        total_dividends=month_total,
                    )
                )

        db.session.commit()
