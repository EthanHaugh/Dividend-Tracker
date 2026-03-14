import logging
from datetime import datetime
from functools import wraps
from celery_app import celery
from services.sync_service import (
    download_and_process_report,
    request_dividend_report,
    sync_account_summary,
    sync_company_dividends,
    sync_open_positions,
)

logger = logging.getLogger(__name__)


def run_task(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"Starting {func.__name__}")
        try:
            result = func(*args, **kwargs)
            logger.info(f"{func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"{func.__name__} failed with error: {e}", exc_info=True)
            raise

    return wrapper


@celery.task
@run_task
def sync_positions_task():
    """
    Fetch currently open positons from Trading212 and update the database
    """

    sync_open_positions()


@celery.task
@run_task
def sync_account_summary_task():
    """
    Fetch Account Summary data from Trading212 and update the database
    """

    sync_account_summary()


@celery.task
@run_task
def download_dividend_report_task(report_id: int, year: int):
    """Downloads and processes the report after the initial delay."""
    download_and_process_report(report_id, year)
    sync_company_dividends_task.delay()


@celery.task
@run_task
def sync_dividend_history_task(year: int | None = None):
    if year is None:
        year = datetime.now().year
    report_id = request_dividend_report(year)
    download_dividend_report_task.apply_async(
        args=[report_id, year],
        # Allow Trading212 to process the report before kicking the job off
        countdown=25,
    )


@celery.task
@run_task
def sync_company_dividends_task(year: int | None = None):
    """
    Check that the Companys tables `total_payment` is
    up to date with the existing dividends
    """

    sync_company_dividends()
