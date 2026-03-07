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
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import db


class Company(db.Model):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True)
    ticker = Column(String(20), unique=True, nullable=False)
    name = Column(String(100), unique=True, nullable=False, index=True)
    quantity = Column(Float, nullable=False)
    initial_buy_date = Column(Date, nullable=False)
    average_buy_price = Column(Float, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def asdict(self):
        return {
            "id": self.id,
            "trading212_ticker": self.ticker,
            "name": self.name,
            "quantity": self.quantity,
            "initial_buy_date": self.initial_buy_date,
            "average_buy_price": self.average_buy_price,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class Dividend(db.Model):
    __tablename__ = "dividends"

    dividend_id = Column(Integer, primary_key=True)
    report_id = Column(
        Integer, ForeignKey("dividend_reports.report_id"), nullable=False
    )
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    payment_date = Column(Date, nullable=False)
    year = Column(Integer, nullable=False)
    total_payment = Column(Numeric(10, 4), nullable=False)
    number_of_shares = Column(Float, nullable=False)
    currency = Column(String(10))
    created_at = Column(DateTime, server_default=func.now())

    company = relationship("Company", backref="dividends")

    def asdict(self):
        return {
            "dividend_id": self.dividend_id,
            "report_id": self.report_id,
            "company_id": self.company_id,
            "company_name": self.company.name if self.company else None,
            "ticker": self.company.ticker if self.company else None,
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
    total_dividends: Mapped[float] = mapped_column(
        Float, server_default="0.0", nullable=False
    )
    created_at = Column(DateTime, server_default=func.now())
    yoy_increase: Mapped[float] = mapped_column(
        Float, server_default="0.0", nullable=False
    )

    def asdict(self):
        return {
            "id": self.id,
            "year": self.year,
            "total_dividends": self.total_dividends,
            "yoy_increase": self.yoy_increase,
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
