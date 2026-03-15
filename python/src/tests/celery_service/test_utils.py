import io
from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock, patch

from celery_service.services.utils import (
    process_dividend_csv,
    calculate_estimated_deposits,
)
from database.models import Company

import pytest

MODULE = "celery_service.services.utils"

CSV_HEADERS = "Action,Time,Name,No. of shares,Price / share,Currency (Price / share),Exchange rate,Total,Withholding tax,Currency (Withholding tax),Notes\n"


def make_csv(*rows: dict) -> str:
    """Build a minimal dividend CSV string from a list of row dicts."""
    lines = [CSV_HEADERS]
    for row in rows:
        lines.append(
            f"Dividend,{row.get('Time', '2024-03-01T00:00:00')},{row.get('Name', 'Apple Inc.')},"
            f"{row.get('No. of shares', '10')},{row.get('Price / share', '1.00')},"
            f"{row.get('Currency (Price / share)', 'USD')},1.0,"
            f"{row.get('Total', '10.00')},0,USD,\n"
        )
    return "".join(lines)


@pytest.fixture
def mock_db_session():
    with patch(f"{MODULE}.db") as mock_db:
        mock_db.session = MagicMock()
        yield mock_db.session


class TestCalculateEstimatedDeposits:
    def test_basic_calculation(self):
        result = calculate_estimated_deposits(
            total_cost=10000.0,
            total_dividends=500.0,
            realised_profit_loss=200.0,
        )

        assert isinstance(result, Decimal)
        assert result == Decimal("9300.0")

    def test_zero_dividends_and_profit(self):
        result = calculate_estimated_deposits(5000.0, 0.0, 0.0)

        assert result == Decimal("5000.0")

    def test_negative_profit_loss_increases_deposits(self):
        """A realised loss means estimated deposits should be higher."""

        result = calculate_estimated_deposits(
            total_cost=10000.0,
            total_dividends=0.0,
            realised_profit_loss=-500.0,
        )

        assert result == Decimal("10500.0")

    def test_floating_point_precision(self):
        """Ensures Decimal conversion avoids float precision errors."""

        result = calculate_estimated_deposits(1000.10, 0.01, 0.01)

        assert result == Decimal("1000.08")


class TestProcessDividendCsv:
    def _setup_placeholder(self, mock_db_session):
        placeholder = MagicMock()
        placeholder.id = 0
        placeholder.total_payments = Decimal("0")
        mock_db_session.query.return_value.filter.return_value.one.return_value = (
            placeholder
        )
        return placeholder

    def _setup_company_lookup(self, mock_db_session, company=None):
        mock_db_session.query.return_value.filter.return_value.one_or_none.return_value = company

    def test_adds_dividend_for_known_company(self, mock_db_session):
        known_company = MagicMock(id=1, total_payments=Decimal("0"))
        placeholder = self._setup_placeholder(mock_db_session)

        query_mock = MagicMock()
        query_mock.filter.return_value.one.return_value = placeholder
        query_mock.filter.return_value.one_or_none.return_value = known_company

        mock_db_session.query.return_value = query_mock

        csv_content = make_csv({"Name": "Apple Inc.", "Total": "15.00"})

        with patch("builtins.open", return_value=io.StringIO(csv_content)):
            process_dividend_csv("dividends.csv", report_id=1, year=2024)

        added = mock_db_session.add.call_args_list[0][0][0]
        assert added.company_id == known_company.id
        assert added.total_payment == Decimal("15.00")

    def test_falls_back_to_placeholder_for_unknown_company(self, mock_db_session):
        placeholder = MagicMock(id=0, total_payments=Decimal("0"))

        query_mock = MagicMock()
        query_mock.filter.return_value.one.return_value = placeholder
        query_mock.filter.return_value.one_or_none.return_value = None

        mock_db_session.query.return_value = query_mock

        csv_content = make_csv({"Name": "Unknown Corp", "Total": "5.00"})

        with patch("builtins.open", return_value=io.StringIO(csv_content)):
            process_dividend_csv("dividends.csv", report_id=1, year=2024)

        added = mock_db_session.add.call_args_list[0][0][0]
        assert added.company_id == placeholder.id

    def test_accumulates_total_payments_on_company(self, mock_db_session):
        known_company = MagicMock(id=1, total_payments=Decimal("10.00"))
        placeholder = MagicMock(id=0, total_payments=Decimal("0"))

        query_mock = MagicMock()
        query_mock.filter.return_value.one.return_value = placeholder
        query_mock.filter.return_value.one_or_none.return_value = known_company

        mock_db_session.query.return_value = query_mock

        csv_content = make_csv(
            {"Name": "Apple Inc.", "Total": "5.00"},
            {"Name": "Apple Inc.", "Total": "7.00"},
        )

        with patch("builtins.open", return_value=io.StringIO(csv_content)):
            process_dividend_csv("dividends.csv", report_id=1, year=2024)

        assert known_company.total_payments == Decimal("22.00")

    def test_accumulates_payments_on_placeholder_for_unknown(self, mock_db_session):
        placeholder = MagicMock(id=0, total_payments=Decimal("0"))

        query_mock = MagicMock()
        query_mock.filter.return_value.one.return_value = placeholder
        query_mock.filter.return_value.one_or_none.return_value = None

        mock_db_session.query.return_value = query_mock

        csv_content = make_csv(
            {"Name": "Ghost Corp", "Total": "3.00"},
            {"Name": "Ghost Corp", "Total": "4.00"},
        )

        with patch("builtins.open", return_value=io.StringIO(csv_content)):
            process_dividend_csv("dividends.csv", report_id=1, year=2024)

        assert placeholder.total_payments == Decimal("7.00")

    def test_calculates_yoy_increase_correctly(self, mock_db_session):
        placeholder = MagicMock(id=0, total_payments=Decimal("0"))
        previous_year = MagicMock(total_dividends=Decimal("100.00"))

        def query_side_effect(model):
            mock = MagicMock()
            if model is Company:
                mock.filter.return_value.one.return_value = placeholder
                mock.filter.return_value.one_or_none.return_value = None
            else:
                mock.filter.return_value.one_or_none.return_value = previous_year
            return mock

        mock_db_session.query.side_effect = query_side_effect

        csv_content = make_csv({"Total": "150.00"})

        with patch("builtins.open", return_value=io.StringIO(csv_content)):
            process_dividend_csv("dividends.csv", report_id=1, year=2024)

        yearly = mock_db_session.add.call_args_list[-1][0][0]
        assert yearly.yoy_increase == 50.0

    def test_yoy_increase_is_zero_when_no_previous_year(self, mock_db_session):
        placeholder = MagicMock(id=0, total_payments=Decimal("0"))

        query_mock = MagicMock()
        query_mock.filter.return_value.one.return_value = placeholder
        query_mock.filter.return_value.one_or_none.return_value = None

        mock_db_session.query.return_value = query_mock

        csv_content = make_csv({"Total": "100.00"})

        with patch("builtins.open", return_value=io.StringIO(csv_content)):
            process_dividend_csv("dividends.csv", report_id=1, year=2024)

        yearly = mock_db_session.add.call_args_list[-1][0][0]
        assert yearly.yoy_increase == 0.0

    def test_yoy_increase_is_zero_when_previous_year_total_is_zero(
        self, mock_db_session
    ):
        placeholder = MagicMock(id=0, total_payments=Decimal("0"))
        previous_year = MagicMock(total_dividends=Decimal("0"))

        query_mock = MagicMock()
        query_mock.filter.return_value.one.return_value = placeholder
        # first one_or_none = company lookup, second = previous year
        query_mock.filter.return_value.one_or_none.side_effect = [None, previous_year]

        mock_db_session.query.return_value = query_mock

        csv_content = make_csv({"Total": "100.00"})

        with patch("builtins.open", return_value=io.StringIO(csv_content)):
            process_dividend_csv("dividends.csv", report_id=1, year=2024)

        yearly = mock_db_session.add.call_args_list[-1][0][0]
        assert yearly.yoy_increase == 0.0

    def test_commits_after_all_rows_processed(self, mock_db_session):
        placeholder = MagicMock(id=0, total_payments=Decimal("0"))

        query_mock = MagicMock()
        query_mock.filter.return_value.one.return_value = placeholder
        query_mock.filter.return_value.one_or_none.return_value = None

        mock_db_session.query.return_value = query_mock

        csv_content = make_csv(
            {"Total": "10.00"},
            {"Total": "20.00"},
            {"Total": "30.00"},
        )

        with patch("builtins.open", return_value=io.StringIO(csv_content)):
            process_dividend_csv("dividends.csv", report_id=1, year=2024)

        mock_db_session.commit.assert_called_once()

    def test_adds_yearly_dividends_row_with_correct_totals(self, mock_db_session):
        placeholder = MagicMock(id=0, total_payments=Decimal("0"))

        query_mock = MagicMock()
        query_mock.filter.return_value.one.return_value = placeholder
        query_mock.filter.return_value.one_or_none.return_value = None

        mock_db_session.query.return_value = query_mock

        csv_content = make_csv(
            {"Total": "40.00"},
            {"Total": "60.00"},
        )

        with patch("builtins.open", return_value=io.StringIO(csv_content)):
            process_dividend_csv("dividends.csv", report_id=1, year=2024)

        yearly = mock_db_session.add.call_args_list[-1][0][0]
        assert yearly.year == 2024
        assert yearly.total_dividends == 100.0

    def test_dividend_payment_date_parsed_correctly(self, mock_db_session):
        placeholder = MagicMock(id=0, total_payments=Decimal("0"))

        query_mock = MagicMock()
        query_mock.filter.return_value.one.return_value = placeholder
        query_mock.filter.return_value.one_or_none.return_value = None

        mock_db_session.query.return_value = query_mock

        csv_content = make_csv({"Time": "2024-06-15T12:30:00", "Total": "10.00"})

        with patch("builtins.open", return_value=io.StringIO(csv_content)):
            process_dividend_csv("dividends.csv", report_id=1, year=2024)

        dividend = mock_db_session.add.call_args_list[0][0][0]
        assert dividend.payment_date == datetime(2024, 6, 15, 12, 30, 0)
        assert dividend.year == 2024

    def test_dividend_uses_correct_report_id(self, mock_db_session):
        placeholder = MagicMock(id=0, total_payments=Decimal("0"))

        query_mock = MagicMock()
        query_mock.filter.return_value.one.return_value = placeholder
        query_mock.filter.return_value.one_or_none.return_value = None

        mock_db_session.query.return_value = query_mock

        csv_content = make_csv()

        with patch("builtins.open", return_value=io.StringIO(csv_content)):
            process_dividend_csv("dividends.csv", report_id=42, year=2024)

        # No dividends added for an empty CSV — only YearlyDividends
        yearly = mock_db_session.add.call_args_list[0][0][0]
        assert yearly.year == 2024

    def test_empty_csv_adds_yearly_dividends_with_zero_total(self, mock_db_session):
        placeholder = MagicMock(id=0, total_payments=Decimal("0"))

        query_mock = MagicMock()
        query_mock.filter.return_value.one.return_value = placeholder
        query_mock.filter.return_value.one_or_none.return_value = None

        mock_db_session.query.return_value = query_mock

        with patch("builtins.open", return_value=io.StringIO(CSV_HEADERS)):
            process_dividend_csv("dividends.csv", report_id=1, year=2024)

        mock_db_session.add.assert_called_once()
        yearly = mock_db_session.add.call_args_list[0][0][0]
        assert yearly.total_dividends == 0.0
        assert yearly.yoy_increase == 0.0
