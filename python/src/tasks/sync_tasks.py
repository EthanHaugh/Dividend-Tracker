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
    """
    Fetch currently open positons from Trading212 and update the database
    """
    
    sync_open_positions()


@run_task
@celery.task
def sync_account_summary_task():
    """
    Fetch Account Summary data from Trading212 and update the database
    """

    sync_account_summary()


@celery.task
@run_task
def sync_dividend_history_task(year: int | None = None):
    """
    Request, Download and Process CSV from Trading212

    This is a scheduled job (see config.py) and also can
    be run on demand via the `/download` endpoint
    """
    if year is None:
        year = datetime.now().year

    sync_dividend_history(year)
