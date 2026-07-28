from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from app import create_app
from database.models import Company
from routes.endpoints import SortDirection, _sort_query, _vaidate_sort_by

MODULE = "routes.endpoints"


@pytest.fixture
def app():
    app = create_app("TESTING")
    app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        }
    )
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def mock_db(app):
    with app.app_context():
        with patch(f"{MODULE}.db") as mock:
            mock.session = MagicMock()
            yield mock.session


def make_company(**kwargs):
    defaults = {
        "id": 1,
        "ticker": "AAPL",
        "name": "Apple Inc.",
        "quantity": 10.0,
        "average_buy_price": Decimal("150.00"),
        "total_payments": Decimal("100.00"),
        "initial_buy_date": "2023-01-01",
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00",
    }
    defaults.update(kwargs)
    company = MagicMock()
    company.asdict.return_value = defaults
    for k, v in defaults.items():
        setattr(company, k, v)
    return company


def make_yearly_dividend(**kwargs):
    defaults = {
        "id": 1,
        "year": 2024,
        "total_dividends": Decimal("500.00"),
        "yoy_increase": Decimal("10.00"),
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00",
    }
    defaults.update(kwargs)
    yd = MagicMock()
    yd.asdict.return_value = defaults
    for k, v in defaults.items():
        setattr(yd, k, v)
    return yd


def make_dividend(**kwargs):
    defaults = {
        "dividend_id": 1,
        "report_id": 1,
        "company_id": 1,
        "company_name": "Apple Inc.",
        "ticker": "AAPL",
        "payment_date": "2024-03-01",
        "year": 2024,
        "total_payment": Decimal("15.00"),
        "number_of_shares": 10.0,
        "currency": "USD",
        "created_at": "2024-01-01T00:00:00",
    }
    defaults.update(kwargs)
    d = MagicMock()
    d.asdict.return_value = defaults
    for k, v in defaults.items():
        setattr(d, k, v)
    return d


class TestValidateSortBy:
    def test_returns_true_for_valid_field(self):
        assert _vaidate_sort_by("name", ["name", "total_payments"]) is True

    def test_returns_false_for_invalid_field(self):
        assert _vaidate_sort_by("injected_field", ["name", "total_payments"]) is False

    def test_returns_true_when_sort_by_is_none(self):
        assert _vaidate_sort_by(None, ["name", "total_payments"]) is True

    def test_returns_true_when_sort_by_is_empty_string(self):
        assert _vaidate_sort_by("", ["name", "total_payments"]) is True


class TestSortQuery:
    def test_applies_descending_order(self):
        query = MagicMock()
        _sort_query(query, Company, "name", SortDirection.DESCENDING)

        query.order_by.assert_called_once()

    def test_applies_ascending_order(self):
        query = MagicMock()
        _sort_query(query, Company, "name", SortDirection.ASCENDING)

        query.order_by.assert_called_once()


class TestHealthCheck:
    def test_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_returns_healthy_status(self, client):
        response = client.get("/health")
        assert response.get_json() == {"status": "healthy"}


class TestGetOpenPositions:
    def test_returns_200_with_companies(self, client, mock_db):
        companies = [make_company(ticker="AAPL"), make_company(ticker="MSFT", id=2)]
        mock_db.query.return_value.all.return_value = companies

        response = client.get("/open-positions")

        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 2

    def test_returns_empty_list_when_no_companies(self, client, mock_db):
        mock_db.query.return_value.all.return_value = []

        response = client.get("/open-positions")

        assert response.status_code == 200
        assert response.get_json() == []


class TestGetYearlyDividends:
    def test_returns_all_yearly_dividends(self, client, mock_db):
        yearly = [
            make_yearly_dividend(year=2023),
            make_yearly_dividend(year=2024, id=2),
        ]
        mock_db.query.return_value.order_by.return_value.all.return_value = yearly

        response = client.get("/yearly-dividends")

        assert response.status_code == 200
        assert len(response.get_json()) == 2

    def test_returns_single_year_when_year_param_given(self, client, mock_db):
        yd = make_yearly_dividend(year=2024)
        mock_db.query.return_value.order_by.return_value.filter.return_value.one_or_none.return_value = yd

        response = client.get("/yearly-dividends?year=2024")

        assert response.status_code == 200
        data = response.get_json()
        assert data[0]["year"] == 2024

    def test_returns_404_when_year_not_found(self, client, mock_db):
        mock_db.query.return_value.order_by.return_value.filter.return_value.one_or_none.return_value = None

        response = client.get("/yearly-dividends?year=1900")

        assert response.status_code == 404
        assert "error" in response.get_json()


class TestGetTotalDividends:
    def test_returns_total(self, client, mock_db):
        mock_db.query.return_value.scalar.return_value = 1500.00

        response = client.get("/total-dividends")

        assert response.status_code == 200
        assert response.get_json()["total_dividends"] == 1500.00

    def test_returns_zero_when_no_dividends(self, client, mock_db):
        mock_db.query.return_value.scalar.return_value = None

        response = client.get("/total-dividends")

        assert response.status_code == 200
        assert response.get_json()["total_dividends"] == 0


class TestGetAccountCash:
    def test_returns_account_metadata(self, client, mock_db):
        metadata = MagicMock()
        metadata.asdict.return_value = {
            "id": 1,
            "account_value": "12000.00",
            "estimated_deposits": "10000.00",
        }
        mock_db.query.return_value.one_or_none.return_value = metadata

        response = client.get("/account-cash")

        assert response.status_code == 200
        assert response.get_json()["account_value"] == "12000.00"

    def test_returns_404_when_no_metadata(self, client, mock_db):
        mock_db.query.return_value.one_or_none.return_value = None

        response = client.get("/account-cash")

        assert response.status_code == 404
        assert "error" in response.get_json()


class TestGetPieChartData:
    def _make_pie_row(self, name, ticker, total_payment):
        row = MagicMock()
        row.total_payment = total_payment
        row._asdict.return_value = {
            "company_id": 1,
            "name": name,
            "ticker": ticker,
            "total_payment": total_payment,
        }
        return row

    def test_returns_data_with_percentages(self, client, mock_db):
        rows = [
            self._make_pie_row("Apple Inc.", "AAPL", 75.0),
            self._make_pie_row("Microsoft", "MSFT", 25.0),
        ]
        mock_db.query.return_value.join.return_value.group_by.return_value.order_by.return_value.all.return_value = rows

        response = client.get("/pie-chart")

        assert response.status_code == 200
        data = response.get_json()["data"]
        assert data[0]["percentage"] == 75.0
        assert data[1]["percentage"] == 25.0

    def test_percentages_sum_to_100(self, client, mock_db):
        rows = [
            self._make_pie_row("Apple Inc.", "AAPL", 60.0),
            self._make_pie_row("Microsoft", "MSFT", 40.0),
        ]
        mock_db.query.return_value.join.return_value.group_by.return_value.order_by.return_value.all.return_value = rows

        response = client.get("/pie-chart")

        data = response.get_json()["data"]
        total_pct = sum(item["percentage"] for item in data)
        assert total_pct == 100.0

    def test_returns_empty_data_when_no_dividends(self, client, mock_db):
        mock_db.query.return_value.join.return_value.group_by.return_value.order_by.return_value.all.return_value = []

        response = client.get("/pie-chart")

        assert response.status_code == 200
        body = response.get_json()
        assert body["data"] == []
        assert body["total_dividends"] == 0
        assert body["total_count"] == 0


class TestListCompanyTotals:
    def _setup_query_chain(self, mock_db, rows, total_count=None):
        chain = mock_db.query.return_value.join.return_value.group_by.return_value
        chain.count.return_value = total_count if total_count is not None else len(rows)
        chain.order_by.return_value.offset.return_value.limit.return_value.__iter__ = (
            lambda self: iter(rows)
        )
        chain.order_by.return_value.count.return_value = len(rows)
        chain.order_by.return_value.filter.return_value.count.return_value = len(rows)
        chain.order_by.return_value.filter.return_value.filter.return_value.count.return_value = len(
            rows
        )
        chain.order_by.return_value.filter.return_value.filter.return_value.offset.return_value.limit.return_value.__iter__ = (
            lambda self: iter(rows)
        )
        chain.order_by.return_value.filter.return_value.offset.return_value.limit.return_value.__iter__ = (
            lambda self: iter(rows)
        )
        return chain

    def _make_row(self, ticker="AAPL", name="Apple Inc.", total=100.0):
        row = MagicMock()
        row._asdict.return_value = {
            "ticker": ticker,
            "name": name,
            "total_payment": total,
        }
        return row

    def test_returns_paginated_results(self, client, mock_db):
        rows = [self._make_row()]
        self._setup_query_chain(mock_db, rows)

        response = client.get("/list-company-totals")

        assert response.status_code == 200
        body = response.get_json()
        assert "data" in body
        assert body["page"] == 1
        assert body["page_size"] == 10

    def test_returns_400_for_invalid_sort_by(self, client, mock_db):
        response = client.get("/list-company-totals?sort_by=injected_field")

        assert response.status_code == 400
        assert "error" in response.get_json()

    def test_filters_by_ticker(self, client, mock_db):
        rows = [self._make_row(ticker="AAPL")]
        self._setup_query_chain(mock_db, rows)

        response = client.get("/list-company-totals?filters=AAPL")

        assert response.status_code == 200

    def test_applies_search(self, client, mock_db):
        rows = [self._make_row(name="Apple Inc.")]
        self._setup_query_chain(mock_db, rows)

        response = client.get("/list-company-totals?search=apple")

        assert response.status_code == 200

    def test_custom_page_and_page_size(self, client, mock_db):
        rows = [self._make_row()]
        self._setup_query_chain(mock_db, rows)

        response = client.get("/list-company-totals?page=2&page_size=5")

        body = response.get_json()
        assert body["page"] == 2
        assert body["page_size"] == 5


class TestListCompanyDividends:
    def _setup_query_chain(self, mock_db, rows):
        chain = mock_db.query.return_value.join.return_value.where.return_value.filter.return_value
        chain.order_by.return_value.count.return_value = len(rows)
        chain.order_by.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = rows
        chain.count.return_value = len(rows)
        return chain

    def test_returns_400_when_no_ticker(self, client, mock_db):
        response = client.get("/list-company-dividends")

        assert response.status_code == 400
        assert "ticker" in response.get_json()["error"]

    def test_returns_400_for_invalid_sort_by(self, client, mock_db):
        response = client.get("/list-company-dividends?ticker=AAPL&sort_by=injected")

        assert response.status_code == 400
        assert "error" in response.get_json()

    def test_returns_dividends_for_ticker(self, client, mock_db):
        dividends = [make_dividend(), make_dividend(dividend_id=2)]
        self._setup_query_chain(mock_db, dividends)

        response = client.get("/list-company-dividends?ticker=AAPL")

        assert response.status_code == 200
        body = response.get_json()
        assert "data" in body
        assert body["total_count"] == 2

    def test_pagination_defaults(self, client, mock_db):
        self._setup_query_chain(mock_db, [])

        response = client.get("/list-company-dividends?ticker=AAPL")

        body = response.get_json()
        assert body["page"] == 1
        assert body["page_size"] == 10


class TestGetAvailableTickers:
    def test_returns_tickers(self, client, mock_db):
        row1 = MagicMock()
        row1._asdict.return_value = {"ticker": "AAPL", "name": "Apple Inc."}
        row2 = MagicMock()
        row2._asdict.return_value = {"ticker": "MSFT", "name": "Microsoft"}

        (
            mock_db.query.return_value.distinct.return_value.order_by.return_value.all.return_value
        ) = [row1, row2]

        response = client.get("/list-available-tickers")

        assert response.status_code == 200
        data = response.get_json()["data"]
        assert len(data) == 2
        assert data[0]["ticker"] == "AAPL"

    def test_returns_empty_list_when_no_tickers(self, client, mock_db):
        (
            mock_db.query.return_value.distinct.return_value.order_by.return_value.all.return_value
        ) = []

        response = client.get("/list-available-tickers")

        assert response.status_code == 200
        assert response.get_json()["data"] == []


class TestGetMonthlyDividendsComparison:
    @staticmethod
    def _make_year_row(year):
        row = MagicMock()
        row.year = year
        return row

    @staticmethod
    def _make_monthly_row(year, month, total):
        row = MagicMock()
        row.year = year
        row.month = month
        row.total_dividends = total
        return row

    def test_returns_empty_payload_when_no_monthly_data(self, client, mock_db):
        available_query = MagicMock()
        available_query.distinct.return_value.order_by.return_value.all.return_value = []
        mock_db.query.return_value = available_query

        response = client.get("/monthly-dividends-comparison")

        assert response.status_code == 200
        assert response.get_json() == {
            "available_years": [],
            "selected_years": [],
            "data": [],
        }

    def test_returns_zero_filled_month_data_for_selected_years(self, client, mock_db):
        available_query = MagicMock()
        available_query.distinct.return_value.order_by.return_value.all.return_value = [
            self._make_year_row(2023),
            self._make_year_row(2024),
        ]

        monthly_query = MagicMock()
        monthly_query.filter.return_value.all.return_value = [
            self._make_monthly_row(2023, 1, 10.0),
            self._make_monthly_row(2024, 1, 20.0),
            self._make_monthly_row(2024, 2, 5.0),
        ]

        mock_db.query.side_effect = [available_query, monthly_query]

        response = client.get("/monthly-dividends-comparison?years=2023,2024")

        assert response.status_code == 200
        body = response.get_json()
        assert body["available_years"] == [2023, 2024]
        assert body["selected_years"] == [2023, 2024]
        assert len(body["data"]) == 12

        january = body["data"][0]
        february = body["data"][1]
        assert january["month"] == 1
        assert january["values"]["2023"] == 10.0
        assert january["values"]["2024"] == 20.0
        assert february["values"]["2023"] == 0.0
        assert february["values"]["2024"] == 5.0

    def test_returns_400_for_invalid_years_param(self, client, mock_db):
        available_query = MagicMock()
        available_query.distinct.return_value.order_by.return_value.all.return_value = [
            self._make_year_row(2024),
        ]
        mock_db.query.return_value = available_query

        response = client.get("/monthly-dividends-comparison?years=2024,not-a-year")

        assert response.status_code == 400
        assert "error" in response.get_json()

    def test_returns_400_for_unavailable_years(self, client, mock_db):
        available_query = MagicMock()
        available_query.distinct.return_value.order_by.return_value.all.return_value = [
            self._make_year_row(2024),
        ]
        mock_db.query.return_value = available_query

        response = client.get("/monthly-dividends-comparison?years=2023")

        assert response.status_code == 400
        body = response.get_json()
        assert body["invalid_years"] == [2023]
