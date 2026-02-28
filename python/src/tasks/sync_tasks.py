import logging

from celery_app import celery
from services.sync_service import sync_account_summary, sync_open_positions

logger = logging.getLogger(__name__)

def run_task(func):
    def run_and_update():
        logger.info(f"Starting {func.__name__}")
        try:
            func()
            logger.info(f"{func.__name__} completed successfully")
        except Exception as e:
            logger.error(f"{func.__name__} failed with error: {e}", exc_info=True)
            raise

    return run_and_update


@run_task
@celery.task
def sync_positions_task():
    sync_open_positions()

@run_task
@celery.task
def sync_account_summary_task():
    sync_account_summary()
 