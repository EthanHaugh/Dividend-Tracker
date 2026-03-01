from sqlalchemy import (
    Column,
    Float,
    String,
    Integer,
    Numeric,
    Date,
    DateTime,
    ForeignKey,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column
from app.db import db

class Company(db.Model):
    __tablename__ = "companies"

    ticker = Column(String(10), unique=True, primary_key=True)
    name = Column(String(20), unique=True)
    quantity = Column(Float, nullable=False)
    initial_buy_date = Column(Date, nullable=False)
    average_buy_price = Column(Float, nullable=False)

    def asdict(self):
        return {
            "ticker": self.ticker,
            "name": self.name,
            "quantity": self.quantity,
            "initial_buy_date": self.initial_buy_date,
            "average_buy_price": self.average_buy_price,
        }


class Dividend(db.Model):
    __tablename__ = "dividends"

    dividend_id = Column(Integer, primary_key=True)
    report_id = Column(
        Integer, ForeignKey("dividend_reports.report_id"), nullable=False
    )
    ticker = Column(String(10), ForeignKey("companies.ticker"), nullable=False)
    payment_date = Column(Date, nullable=False)
    year = Column(Integer, nullable=False)
    total_payment = Column(Numeric(10, 4), nullable=False)
    number_of_shares = Column(Float, nullable=False)
    currency = Column(String(10))
    created_at = Column(DateTime, server_default=func.now())

    def asdict(self):
        return {
            "dividend_id": self.dividend_id,
            "report_id": self.report_id,
            "ticker": self.ticker,
            "payment_date": self.payment_date,
            "year": self.year,
            "total_payment": self.total_payment,
            "number_of_shares": self.number_of_shares,
            "currency": self.currency,
            "created_at": self.created_at,
        }


class DividendReport(db.Model):
    __tablename__ = "dividend_reports"

    report_id = Column(Integer, primary_key=True)
    time_from = Column(Date, nullable=False)
    time_to = Column(Date, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    def asdict(self):
        return {
            "report_id": self.report_id,
            "time_from": self.time_from,
            "time_to": self.time_to,
            "created_at": self.created_at,
        }


class YearlyDividends(db.Model):
    __tablename__ = "yearly_dividends"

    id = Column(Integer, primary_key=True)
    year = Column(Integer, nullable=False)
    total_dividends = Column(Numeric(10, 4), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    yoy_increase: Mapped[float] = mapped_column(Float, server_default=u'0.0', nullable=False)

    def asdict(self):
        return {
            "id": self.id,
            "year": self.year,
            "total_dividends": self.total_dividends,
            "created_at": self.created_at,
        }


class AccountMetadata(db.Model):
    __tablename__ = "account_metadata"

    id = Column(Integer, primary_key=True)
    account_value: Mapped[float] = mapped_column(Float, nullable=False)
    estimated_deposits: Mapped[float] = mapped_column(Float, nullable=False)

    def asdict(self):
        return {
            "id": self.id,
            "account_value": self.account_value,
            "estimated_deposits": self.estimated_deposits,
        }
