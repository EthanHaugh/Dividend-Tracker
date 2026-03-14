from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Integer,
    String,
    Numeric,
    Date,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.db import Base


class BaseModel:
    """Mixin for common model functionality."""

    def asdict(self):
        """Convert model to dictionary."""
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}


class Company(Base, BaseModel):
    """
    Represents a company/stock held in the portfolio.
    """

    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True)
    ticker: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    quantity: Mapped[float] = mapped_column(nullable=False)
    initial_buy_date: Mapped[datetime] = mapped_column(Date, nullable=False)
    average_buy_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 4),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
    total_payments: Mapped[Decimal] = mapped_column(
        Numeric(14, 4),
        nullable=False,
        default=Decimal("0"),
    )

    # Relationships
    dividends: Mapped[list["Dividend"]] = relationship(
        "Dividend", back_populates="company", cascade="all, delete-orphan"
    )


class DividendReport(Base, BaseModel):
    """
    Represents a dividend reporting period.

    Groups dividend payments within a specific date range.
    """

    __tablename__ = "dividend_reports"

    report_id: Mapped[int] = mapped_column(primary_key=True)
    time_from: Mapped[datetime] = mapped_column(Date, nullable=False)
    time_to: Mapped[datetime] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relationships
    dividends: Mapped[list["Dividend"]] = relationship(
        "Dividend", back_populates="report", cascade="all, delete-orphan"
    )


class Dividend(Base, BaseModel):
    """
    Represents a single dividend payment.

    Tracks individual dividend payments per company,
    linked to both a Company and DividendReport.
    """

    __tablename__ = "dividends"

    dividend_id: Mapped[int] = mapped_column(primary_key=True)
    report_id: Mapped[int] = mapped_column(
        ForeignKey("dividend_reports.report_id"), nullable=False
    )
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)
    payment_date: Mapped[datetime] = mapped_column(Date, nullable=False)
    year: Mapped[int] = mapped_column(nullable=False)
    total_payment: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    number_of_shares: Mapped[float] = mapped_column(nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relationships
    company: Mapped["Company"] = relationship("Company", back_populates="dividends")
    report: Mapped["DividendReport"] = relationship(
        "DividendReport", back_populates="dividends"
    )

    def asdict(self) -> dict:
        """Convert model to dictionary including company name and ticker."""
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


class YearlyDividends(Base, BaseModel):
    """
    Aggregated dividend data per year.

    Stores total dividends received in a given year
    and year-over-year growth metrics.
    """

    __tablename__ = "yearly_dividends"

    id: Mapped[int] = mapped_column(primary_key=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    total_dividends: Mapped[Decimal] = mapped_column(
        Numeric(12, 4), server_default="0.0", nullable=False
    )
    yoy_increase: Mapped[Decimal] = mapped_column(
        Numeric(8, 4),
        server_default="0.0",
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (UniqueConstraint("year", name="uq_yearly_dividends_year"),)


class AccountMetadata(Base, BaseModel):
    """
    Portfolio-level metadata and metrics.

    Tracks overall account value and estimated total deposits
    for performance calculation purposes.
    """

    __tablename__ = "account_metadata"

    id: Mapped[int] = mapped_column(primary_key=True)
    account_value: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    estimated_deposits: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
