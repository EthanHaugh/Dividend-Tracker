import csv
import os
from datetime import datetime
from models.classes import DividendHistory
from sqlalchemy.exc import IntegrityError
from db import Session

from models.models import Company, Dividend, DividendReport, YearlyDividends


def process_report(response_data: DividendHistory, year: int) -> None:
    with Session() as session:
        try:
            session.add(
                DividendReport(
                    report_id=response_data.reportId,
                    time_from=datetime.fromisoformat(response_data.timeFrom),
                    time_to=datetime.fromisoformat(response_data.timeTo),
                    created_at=datetime.now(),
                )
            )
            session.commit()
        except IntegrityError:
            session.rollback()

        with open("downloaded.csv", "r") as file:
            reader = csv.DictReader(file)
            total_count = 0
            for row in reader:
                total_count += float(row["Total"])
                session.add(
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

            session.add(
                YearlyDividends(
                    year=year,
                    total_dividends=total_count,
                )
            )
            session.commit()

    os.remove("downloaded.csv")


def process_company(response_data: dict) -> None:
    with Session() as session:
        for company in response_data:
            # Check for existing company and update
            existing_company: Company = (
                session.query(Company).filter_by(ticker=company["ticker"]).one_or_none()
            )
            if existing_company:
                existing_company.quantity = company["quantity"]
                existing_company.average_buy_price = company["averagePrice"]
            else:
                # If no company is found, add a new row
                session.add(
                    Company(
                        ticker=company["ticker"],
                        quantity=company["quantity"],
                        initial_buy_date=datetime.fromisoformat(
                            company["initialFillDate"]
                        ),
                        average_buy_price=float(company["averagePrice"]),
                    )
                )
        session.commit()

        # Carry out no clean up for no longer open positions for historical data
