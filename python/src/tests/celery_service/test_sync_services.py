from decimal import Decimal
from unittest.mock import MagicMock, mock_open, patch
from celery_service.services.sync_service import (
    sync_open_positions,
    sync_account_summary,
    request_dividend_report,
    download_and_process_report,
    sync_company_dividends,
)

from sqlalchemy.exc import IntegrityError

import pytest

from database.models import AccountMetadata


@pytest.fixture
def mock_db_session():
    """Provides a mock SQLAlchemy session, patched at the service layer."""
    with patch("celery_service.services.sync_service.db") as mock_db:
        mock_db.session = MagicMock()
        yield mock_db.session


@pytest.fixture
def mock_requests():
    with patch("celery_service.services.sync_service.requests") as mock_req:
        yield mock_req


class TestSyncOpenPositions:
    API_PAYLOAD = [
        {
            "instrument": {"ticker": "AAPL", "name": "Apple Inc."},
            "quantity": 10.0,
            "averagePricePaid": 150.00,
            "createdAt": "2023-01-15T00:00:00",
        },
        {
            "instrument": {"ticker": "MSFT", "name": "Microsoft Corp."},
            "quantity": 5.0,
            "averagePricePaid": 280.00,
            "createdAt": "2023-03-10T00:00:00",
        },
    ]

    def test_updates_existing_company(self, mock_db_session, mock_requests):
        mock_requests.get.return_value = MagicMock(
            status_code=200, json=lambda: self.API_PAYLOAD
        )
        existing = MagicMock(spec=["quantity", "average_buy_price"])
        mock_db_session.query.return_value.filter_by.return_value.one_or_none.return_value = existing

        sync_open_positions()

        assert existing.quantity == 5.0
        assert existing.average_buy_price == 280.00
        mock_db_session.commit.assert_called_once()

    def test_creates_new_company_when_not_found(self, mock_db_session, mock_requests):
        mock_requests.get.return_value = MagicMock(
            status_code=200, json=lambda: self.API_PAYLOAD
        )
        mock_db_session.query.return_value.filter_by.return_value.one_or_none.return_value = None

        sync_open_positions()

        assert mock_db_session.add.call_count == len(self.API_PAYLOAD)
        mock_db_session.commit.assert_called_once()

    def test_returns_raise_on_api_failure(self, mock_db_session, mock_requests):
        mock_requests.get.return_value = MagicMock(
            status_code=500, json=lambda: {"error": "server error"}
        )

        with pytest.raises(
            RuntimeError, match="Unable to retrieve open positions from Trading212"
        ):
            sync_open_positions()

        mock_db_session.add.assert_not_called()
        mock_db_session.commit.assert_not_called()


class TestSyncAccountSummary:
    SUMMARY_PAYLOAD = {
        "currency": "USD",
        "id": 1,
        "totalValue": 1000.0,
        "cash": {
            "availableToTrade": 100,
            "inPies": 1000,
            "reservedForOrders": 0,
        },
        "investments": {
            "totalCost": 10000.00,
            "currentValue": 12000.00,
            "realizedProfitLoss": 500.00,
            "unrealizedProfitLoss": 10000.0,
        },
    }

    def _setup_query_chain(
        self, mock_db_session, deposits_total, yearly_total, metadata
    ):
        """Wire up the three sequential .query() calls the function makes."""
        query_meta = MagicMock()
        query_meta.first.return_value = metadata

        query_deposits = MagicMock()
        query_deposits.filter.return_value = query_deposits
        query_deposits.scalar.return_value = deposits_total

        query_yearly = MagicMock()
        query_yearly.filter.return_value = query_yearly
        query_yearly.scalar.return_value = yearly_total

        mock_db_session.query.side_effect = [query_meta, query_deposits, query_yearly]

    def test_creates_metadata_when_none_exists(self, mock_db_session, mock_requests):
        mock_requests.get.return_value = MagicMock(
            status_code=200, json=lambda: self.SUMMARY_PAYLOAD
        )
        self._setup_query_chain(
            mock_db_session,
            deposits_total=1000.0,
            yearly_total=500.0,
            metadata=None,
        )

        sync_account_summary()

        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()

    def test_updates_existing_metadata(self, mock_db_session, mock_requests):
        mock_requests.get.return_value = MagicMock(
            status_code=200, json=lambda: self.SUMMARY_PAYLOAD
        )
        existing_metadata = MagicMock()
        self._setup_query_chain(
            mock_db_session,
            deposits_total=1000.0,
            yearly_total=500.0,
            metadata=existing_metadata,
        )

        sync_account_summary()

        assert existing_metadata.account_value == Decimal("12000.00")
        mock_db_session.add.assert_not_called()
        mock_db_session.commit.assert_called_once()

    def test_returns_raise_on_api_failure(self, mock_db_session, mock_requests):
        mock_requests.get.return_value = MagicMock(
            status_code=401, json=lambda: {"error": "unauthorized"}
        )

        with pytest.raises(
            RuntimeError, match="Unable to retrieve account summary from Trading212"
        ):
            sync_account_summary()

        mock_db_session.commit.assert_not_called()

    def test_handles_zero_yearly_dividends(self, mock_db_session, mock_requests):
        """Ensures the scalar() None fallback to 0.0 is handled correctly."""

        mock_requests.get.return_value = MagicMock(
            status_code=200, json=lambda: self.SUMMARY_PAYLOAD
        )
        self._setup_query_chain(
            mock_db_session,
            deposits_total=1000.0,
            yearly_total=None,
            metadata=None,
        )

        sync_account_summary()

        mock_db_session.add.assert_called_once()

        created = mock_db_session.add.call_args[0][0]
        assert isinstance(created, AccountMetadata)
        assert created.account_value == Decimal("12000.00")
        assert created.estimated_deposits == Decimal("1000.00")
        mock_db_session.commit.assert_called_once()


class TestRequestDividendReport:
    def test_returns_report_id_on_success(self, mock_requests):
        mock_requests.post.return_value = MagicMock(
            status_code=200, json=lambda: {"reportId": 42}
        )

        result = request_dividend_report(2024)

        assert result == 42

    def test_raises_on_api_failure(self, mock_requests):
        mock_requests.post.return_value = MagicMock(
            status_code=500, json=lambda: {"error": "internal error"}
        )

        with pytest.raises(RuntimeError, match="Failed to request Trading 212 report"):
            request_dividend_report(2024)

    def test_raises_when_report_id_missing(self, mock_requests):
        mock_requests.post.return_value = MagicMock(status_code=200, json=lambda: {})

        with pytest.raises(ValueError, match="missing reportId"):
            request_dividend_report(2024)

    def test_posts_correct_date_range_for_year(self, mock_requests):
        mock_requests.post.return_value = MagicMock(
            status_code=200, json=lambda: {"reportId": 7}
        )

        with patch(
            "celery_service.services.sync_service.end_of_or_today",
            return_value="2023-12-31",
        ):
            request_dividend_report(2023)

        _, kwargs = mock_requests.post.call_args
        payload = kwargs["json"]
        assert payload["timeFrom"] == "2023-01-01T00:00:00Z"
        assert payload["timeTo"] == "2023-12-31T00:00:00Z"
        assert payload["dataIncluded"]["includeDividends"] is True
        assert payload["dataIncluded"]["includeOrders"] is False


REPORT_LIST_PAYLOAD = [
    {
        "reportId": 99,
        "downloadLink": "https://example.com/report.csv",
        "timeFrom": "2024-01-01T00:00:00",
        "timeTo": "2024-12-31T00:00:00",
    }
]


class TestDownloadAndProcessReport:
    def _make_responses(self, mock_requests, report_list=None, csv_content=b"csv,data"):
        """Configure requests.get to return the report list then the CSV download."""
        list_response = MagicMock(
            status_code=200,
            json=lambda: (
                report_list if report_list is not None else REPORT_LIST_PAYLOAD
            ),
        )
        csv_response = MagicMock(status_code=200, content=csv_content)
        csv_response.raise_for_status = MagicMock()
        mock_requests.get.side_effect = [list_response, csv_response]

    def test_raises_when_report_list_call_fails(self, mock_db_session, mock_requests):
        mock_requests.get.return_value = MagicMock(
            status_code=500, json=lambda: {"error": "server error"}
        )

        with pytest.raises(RuntimeError, match="Failed to retrieve report list"):
            download_and_process_report(99, 2024)

    def test_raises_when_report_id_not_in_list(self, mock_db_session, mock_requests):
        mock_requests.get.return_value = MagicMock(
            status_code=200, json=lambda: REPORT_LIST_PAYLOAD
        )

        with pytest.raises(ValueError, match="Report 999 not found"):
            download_and_process_report(999, 2024)

    def test_clears_existing_year_data_before_insert(
        self, mock_db_session, mock_requests
    ):
        self._make_responses(mock_requests)
        existing_report = MagicMock()
        mock_db_session.query.return_value.filter.return_value.one_or_none.return_value = existing_report

        with (
            patch("celery_service.services.sync_service.process_dividend_csv"),
            patch("builtins.open", mock_open()),
            patch("celery_service.services.sync_service.os.remove"),
        ):
            download_and_process_report(99, 2024)

        mock_db_session.delete.assert_called_once_with(existing_report)
        assert mock_db_session.execute.call_count == 2  # Dividend + YearlyDividends

    def test_skips_clear_when_no_existing_report(self, mock_db_session, mock_requests):
        self._make_responses(mock_requests)
        mock_db_session.query.return_value.filter.return_value.one_or_none.return_value = None

        with (
            patch("celery_service.services.sync_service.process_dividend_csv"),
            patch("builtins.open", mock_open()),
            patch("celery_service.services.sync_service.os.remove"),
        ):
            download_and_process_report(99, 2024)

        mock_db_session.delete.assert_not_called()

    def test_csv_removed_even_if_process_raises(self, mock_db_session, mock_requests):
        """The finally block must clean up the temp file on failure."""

        self._make_responses(mock_requests)
        mock_db_session.query.return_value.filter.return_value.one_or_none.return_value = None

        with (
            patch(
                "celery_service.services.sync_service.process_dividend_csv",
                side_effect=RuntimeError("parse error"),
            ),
            patch("builtins.open", mock_open()),
            patch("celery_service.services.sync_service.os.remove") as mock_remove,
        ):
            with pytest.raises(RuntimeError, match="parse error"):
                download_and_process_report(99, 2024)

        mock_remove.assert_called_once_with("dividend_99_2024.csv")

    def test_tmp_file_uses_unique_name(self, mock_db_session, mock_requests):
        """Ensures no race condition from a shared 'downloaded.csv' filename."""

        self._make_responses(mock_requests)
        mock_db_session.query.return_value.filter.return_value.one_or_none.return_value = None

        with (
            patch("celery_service.services.sync_service.process_dividend_csv"),
            patch("builtins.open", mock_open()) as mock_file,
            patch("celery_service.services.sync_service.os.remove"),
        ):
            download_and_process_report(99, 2024)

        opened_path = mock_file.call_args[0][0]
        assert "99" in opened_path
        assert "2024" in opened_path
        assert opened_path != "downloaded.csv"

    def test_integrity_error_on_duplicate_report_is_handled(
        self, mock_db_session, mock_requests
    ):
        self._make_responses(mock_requests)
        mock_db_session.query.return_value.filter.return_value.one_or_none.return_value = None
        mock_db_session.commit.side_effect = [IntegrityError("", "", ""), None]

        with (
            patch("celery_service.services.sync_service.process_dividend_csv"),
            patch("builtins.open", mock_open()),
            patch("celery_service.services.sync_service.os.remove"),
        ):
            # Should not raise — IntegrityError is caught and rolled back
            download_and_process_report(99, 2024)

        mock_db_session.rollback.assert_called_once()


class TestSyncCompanyDividends:
    def test_updates_each_company_total_payments(self, mock_db_session):
        company_a = MagicMock(id=1)
        company_b = MagicMock(id=2)
        mock_db_session.query.return_value.all.return_value = [company_a, company_b]

        scalar_mock = MagicMock()
        scalar_mock.side_effect = [Decimal("100.00"), Decimal("250.50")]
        mock_db_session.query.return_value.where.return_value.scalar = scalar_mock

        sync_company_dividends()

        assert company_a.total_payments == Decimal("100.00")
        assert company_b.total_payments == Decimal("250.50")
        mock_db_session.commit.assert_called_once()

    def test_sets_zero_when_company_has_no_dividends(self, mock_db_session):
        company = MagicMock(id=1)
        mock_db_session.query.return_value.all.return_value = [company]

        scalar_mock = MagicMock()
        scalar_mock.return_value = None
        mock_db_session.query.return_value.where.return_value.scalar = scalar_mock

        sync_company_dividends()

        assert company.total_payments == Decimal(0)
        mock_db_session.commit.assert_called_once()

    def test_commits_once_for_all_companies(self, mock_db_session):
        companies = [MagicMock(id=i) for i in range(5)]
        mock_db_session.query.return_value.all.return_value = companies

        scalar_mock = MagicMock(return_value=Decimal("50.00"))
        mock_db_session.query.return_value.where.return_value.scalar = scalar_mock

        sync_company_dividends()

        mock_db_session.commit.assert_called_once()

    def test_no_commit_when_no_companies(self, mock_db_session):
        mock_db_session.query.return_value.all.return_value = []

        sync_company_dividends()

        mock_db_session.commit.assert_called_once()
