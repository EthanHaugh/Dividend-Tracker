from enum import Enum

from pydantic import BaseModel, Field


class SortDirection(Enum):
    ASCENDING = "ascend"
    DESCENDING = "descend"


class YearlyDividendsParams(BaseModel):
    year: int | None = Field(default=None)


class MonthlyDividendComparisonParams(BaseModel):
    years: list[int] | None = Field(default=None)


class ListCompanyTotalsParams(BaseModel):
    page: int = Field(default=1)
    page_size: int = Field(default=10)
    search: str | None = Field(default=None)
    filters: list[str] | None = Field(default=None)
    sort_by: str = Field(default="total_payments")
    sort_direction: SortDirection = Field(default=SortDirection.DESCENDING)


class ListCompanyDividendsParams(BaseModel):
    page: int = Field(default=1)
    page_size: int = Field(default=10)
    ticker: str | None = Field(default=None)
    sort_by: str = Field(default="payment_date")
    sort_direction: SortDirection = Field(default=SortDirection.ASCENDING)


class ListAvailableTickersParams(BaseModel):
    sort_direction: SortDirection = Field(default=SortDirection.ASCENDING)


class DividendProjectionParams(BaseModel):
    annual_contributions: int = Field(default=0)
    reinvest: bool = Field(default=True)
    years: int = Field(default=10)
