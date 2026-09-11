from datetime import UTC, date, datetime
from decimal import Decimal

from database.db import db
from database.models import (
    AccountMetadata,
    AccountTransactions,
    Company,
    Dividend,
    DividendReport,
    MonthlyDividends,
    TransactionType,
    YearlyDividends,
)

COMPANIES = (
    ("ACME", "Acme Industries", Decimal("82.50"), 85.0),
    ("BRIO", "Brio Consumer Group", Decimal("48.75"), 120.0),
    ("CRES", "Crest Utilities", Decimal("36.20"), 150.0),
)
YEARS = (2022, 2023, 2024, 2025)
PAYMENT_MONTHS = (3, 6, 9, 12)


def seed_demo_data() -> None:
    """Replace all dashboard data with a synthetic portfolio."""
    db.session.query(Dividend).delete()
    db.session.query(DividendReport).delete()
    db.session.query(MonthlyDividends).delete()
    db.session.query(YearlyDividends).delete()
    db.session.query(AccountTransactions).delete()
    db.session.query(AccountMetadata).delete()
    db.session.query(Company).delete()

    companies = [
        Company(
            ticker=ticker,
            name=name,
            quantity=quantity,
            initial_buy_date=date(2022, 1, 10),
            average_buy_price=price,
            total_payments=Decimal(0),
        )
        for ticker, name, price, quantity in COMPANIES
    ]
    db.session.add_all(companies)
    db.session.flush()

    report = DividendReport(time_from=date(2022, 1, 1), time_to=date(2025, 12, 31))
    db.session.add(report)
    db.session.flush()

    yearly_totals = {year: Decimal(0) for year in YEARS}
    monthly_totals = {
        (year, month): Decimal(0) for year in YEARS for month in range(1, 13)
    }
    for company_index, company in enumerate(companies, start=1):
        company_total = Decimal(0)
        for year_index, year in enumerate(YEARS):
            for month_index, month in enumerate(PAYMENT_MONTHS, start=1):
                payment = Decimal(10 + company_index * 4 + year_index * 2 + month_index)
                dividend = Dividend(
                    report_id=report.report_id,
                    company_id=company.id,
                    payment_date=date(year, month, 15),
                    year=year,
                    total_payment=payment,
                    number_of_shares=company.quantity,
                    currency="USD",
                )
                db.session.add(dividend)
                company_total += payment
                yearly_totals[year] += payment
                monthly_totals[(year, month)] += payment
        company.total_payments = company_total

    db.session.add_all(
        [
            YearlyDividends(
                year=year,
                total_dividends=total,
                yoy_increase=(
                    Decimal(0)
                    if year == YEARS[0]
                    else (total - yearly_totals[year - 1])
                    / yearly_totals[year - 1]
                    * 100
                ),
            )
            for year, total in yearly_totals.items()
        ]
    )
    db.session.add_all(
        [
            MonthlyDividends(year=year, month=month, total_dividends=total)
            for (year, month), total in monthly_totals.items()
        ]
    )
    db.session.add(
        AccountMetadata(
            account_value=Decimal("38500.00"),
            estimated_deposits=Decimal("31000.00"),
            estimated_contribution_year=Decimal("8000.00"),
            initial_deposit_date=datetime(2022, 1, 10, tzinfo=UTC),
        )
    )
    db.session.add_all(
        [
            AccountTransactions(
                id="demo-deposit-2022",
                transaction_date=datetime(2022, 1, 10, tzinfo=UTC),
                transaction_amount=Decimal("10000.00"),
                transaction_type=TransactionType.DEPOSIT,
            ),
            AccountTransactions(
                id="demo-deposit-2023",
                transaction_date=datetime(2023, 5, 10, tzinfo=UTC),
                transaction_amount=Decimal("9000.00"),
                transaction_type=TransactionType.DEPOSIT,
            ),
            AccountTransactions(
                id="demo-deposit-2024",
                transaction_date=datetime(2024, 9, 10, tzinfo=UTC),
                transaction_amount=Decimal("12000.00"),
                transaction_type=TransactionType.DEPOSIT,
            ),
        ]
    )
    db.session.commit()
