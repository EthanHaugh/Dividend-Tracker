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
from sqlalchemy.orm import declarative_base, Mapped, mapped_column

Base = declarative_base()


class Company(Base):
    __tablename__ = "companies"

    ticker = Column(String(10), unique=True, primary_key=True)
    quantity = Column(Float, nullable=False)
    initial_buy_date = Column(Date, nullable=False)
    average_buy_price = Column(Float, nullable=False)

    def asdict(self):
        return {
            "ticker": self.ticker,
            "quantity": self.quantity,
            "initial_buy_date": self.initial_buy_date,
            "average_buy_price": self.average_buy_price,
        }


class Dividend(Base):
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


class DividendReport(Base):
    __tablename__ = "dividend_reports"

    report_id = Column(Integer, primary_key=True)
    time_from = Column(DateTime, nullable=False)
    time_to = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    def asdict(self):
        return {
            "report_id": self.report_id,
            "time_from": self.time_from,
            "time_to": self.time_to,
            "created_at": self.created_at,
        }


class YearlyDividends(Base):
    __tablename__ = "yearly_dividends"

    id = Column(Integer, primary_key=True)
    year = Column(Integer, nullable=False)
    total_dividends = Column(Numeric(10, 4), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    def asdict(self):
        return {
            "id": self.id,
            "year": self.year,
            "total_dividends": self.total_dividends,
            "created_at": self.created_at,
        }


class AccountMetadata(Base):
    __tablename__ = "account_metadata"

    id = Column(Integer, primary_key=True)
    account_value: Mapped[float] = mapped_column(Float, nullable=False)

    def asdict(self):
        return {
            "id": self.id,
            "account_value": self.account_value,
        }
