from datetime import datetime
from unittest.mock import patch
from celery_service.tasks.sync_tasks import (
    run_task,
    sync_account_transactions_task,
    sync_dividend_history_task,
    download_dividend_report_task,
    sync_company_dividends_task,
    sync_positions_task,
    sync_account_summary_task,
)
from celery_service.celery_app import celery

import logging
import pytest

TASK_MODULE = "celery_service.tasks.sync_tasks"


class TestRunTaskDecorator:
    def test_logs_start_and_success(self, caplog):
        @run_task
        def sample():
            return "ok"

        with caplog.at_level(logging.INFO):
            sample()

        messages = [r.message for r in caplog.records]
        assert any("Starting sample" in m for m in messages)
        assert any("sample completed successfully" in m for m in messages)

    def test_returns_underlying_value(self):

        @run_task
        def sample():
            return 42

        assert sample() == 42

    def test_logs_error_and_reraises_on_exception(self, caplog):
        @run_task
        def failing():
            raise ValueError("boom")

        with caplog.at_level(logging.ERROR):
            with pytest.raises(ValueError, match="boom"):
                failing()

        assert any("failing failed with error" in r.message for r in caplog.records)

    def test_preserves_function_name(self):
        @run_task
        def my_named_function():
            pass

        assert my_named_function.__name__ == "my_named_function"


class TestSyncPositionsTask:
    def test_calls_sync_open_positions(self):
        with patch(f"{TASK_MODULE}.sync_open_positions") as mock_sync:
            sync_positions_task.run()

            mock_sync.assert_called_once()

    def test_is_registered_as_celery_task(self):
        assert "celery_service.tasks.sync_tasks.sync_positions_task" in celery.tasks

    def test_propagates_exception(self):
        with patch(
            f"{TASK_MODULE}.sync_open_positions", side_effect=RuntimeError("api down")
        ):
            with pytest.raises(RuntimeError, match="api down"):
                sync_positions_task.run()


class TestSyncAccountSummaryTask:
    def test_calls_sync_account_summary(self):
        with patch(f"{TASK_MODULE}.sync_account_summary") as mock_sync:
            sync_account_summary_task.run()

            mock_sync.assert_called_once()

    def test_is_registered_as_celery_task(self):
        assert (
            "celery_service.tasks.sync_tasks.sync_account_summary_task" in celery.tasks
        )

    def test_propagates_exception(self):
        with patch(
            f"{TASK_MODULE}.sync_account_summary", side_effect=RuntimeError("timeout")
        ):
            with pytest.raises(RuntimeError, match="timeout"):
                sync_account_summary_task.run()


class TestSyncDividendHistoryTask:
    def test_uses_current_year_when_none_given(self):
        with (
            patch(
                f"{TASK_MODULE}.request_dividend_report", return_value=99
            ) as mock_request,
            patch(f"{TASK_MODULE}.download_dividend_report_task"),
        ):
            sync_dividend_history_task.run(year=None)

            mock_request.assert_called_once_with(datetime.now().year)

    def test_uses_provided_year(self):
        with (
            patch(
                f"{TASK_MODULE}.request_dividend_report", return_value=42
            ) as mock_request,
            patch(f"{TASK_MODULE}.download_dividend_report_task"),
        ):
            sync_dividend_history_task.run(year=2022)

            mock_request.assert_called_once_with(2022)

    def test_schedules_download_task_with_countdown(self):
        with (
            patch(f"{TASK_MODULE}.request_dividend_report", return_value=7),
            patch(f"{TASK_MODULE}.download_dividend_report_task") as mock_download,
        ):
            sync_dividend_history_task.run(year=2023)

            mock_download.apply_async.assert_called_once_with(
                args=[7, 2023],
                countdown=25,
            )

    def test_passes_report_id_from_request_to_download(self):
        with (
            patch(f"{TASK_MODULE}.request_dividend_report", return_value=55),
            patch(f"{TASK_MODULE}.download_dividend_report_task") as mock_download,
        ):
            sync_dividend_history_task.run(year=2024)

            args = mock_download.apply_async.call_args
            assert args.kwargs["args"][0] == 55  # report_id

    def test_propagates_exception_from_request(self):
        with (
            patch(
                f"{TASK_MODULE}.request_dividend_report",
                side_effect=RuntimeError("T212 unavailable"),
            ),
            patch(f"{TASK_MODULE}.download_dividend_report_task"),
        ):
            with pytest.raises(RuntimeError, match="T212 unavailable"):
                sync_dividend_history_task.run(year=2024)

    def test_is_registered_as_celery_task(self):
        assert (
            "celery_service.tasks.sync_tasks.sync_dividend_history_task" in celery.tasks
        )


class TestDownloadDividendReportTask:
    def test_calls_download_and_process_with_args(self):
        with (
            patch(f"{TASK_MODULE}.download_and_process_report") as mock_download,
            patch(f"{TASK_MODULE}.sync_company_dividends_task"),
        ):
            download_dividend_report_task.run(report_id=99, year=2024)

            mock_download.assert_called_once_with(99, 2024)

    def test_chains_to_sync_company_dividends(self):
        with (
            patch(f"{TASK_MODULE}.download_and_process_report"),
            patch(f"{TASK_MODULE}.sync_company_dividends_task") as mock_sync,
        ):
            download_dividend_report_task.run(report_id=99, year=2024)

            mock_sync.delay.assert_called_once()

    def test_does_not_chain_if_download_raises(self):
        with (
            patch(
                f"{TASK_MODULE}.download_and_process_report",
                side_effect=RuntimeError("download failed"),
            ),
            patch(f"{TASK_MODULE}.sync_company_dividends_task") as mock_sync,
        ):
            with pytest.raises(RuntimeError, match="download failed"):
                download_dividend_report_task.run(report_id=99, year=2024)

            mock_sync.delay.assert_not_called()

    def test_is_registered_as_celery_task(self):
        assert (
            "celery_service.tasks.sync_tasks.download_dividend_report_task"
            in celery.tasks
        )


class TestSyncCompanyDividendsTask:
    def test_calls_sync_company_dividends(self):
        with patch(f"{TASK_MODULE}.sync_company_dividends") as mock_sync:
            sync_company_dividends_task.run()

            mock_sync.assert_called_once()

    def test_is_registered_as_celery_task(self):
        assert (
            "celery_service.tasks.sync_tasks.sync_company_dividends_task"
            in celery.tasks
        )

    def test_propagates_exception(self):
        with patch(
            f"{TASK_MODULE}.sync_company_dividends",
            side_effect=RuntimeError("db error"),
        ):
            with pytest.raises(RuntimeError, match="db error"):
                sync_company_dividends_task.run()


class TestSyncAccountTransactionTask:
    def test_calls_sync_account_transactions(self):
        with patch(f"{TASK_MODULE}.sync_account_transactions") as mock_sync:
            sync_account_transactions_task.run()

            mock_sync.assert_called_once()

    def test_is_registered_as_celery_task(self):
        assert (
            "celery_service.tasks.sync_tasks.sync_account_transactions_task"
            in celery.tasks
        )
