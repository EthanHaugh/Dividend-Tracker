import logging
from datetime import datetime
from functools import wraps
from celery_app import celery
from services.sync_service import (
    sync_account_summary,
    sync_dividend_history,
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


@run_task
@celery.task
def sync_positions_task():
    sync_open_positions()


@run_task
@celery.task
def sync_account_summary_task():
    sync_account_summary()


@celery.task
@run_task
def sync_dividend_history_task(year: int | None = None):
    if year is None:
        year = datetime.now().year

    sync_dividend_history(year)