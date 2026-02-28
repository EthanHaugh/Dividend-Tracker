import logging

from celery_app import celery
from services.sync_service import sync_open_positions

logger = logging.getLogger(__name__)

@celery.task
def sync_positions_task():
    logger.info("Starting sync_positions_task")
    try:
        result = sync_open_positions()
        logger.info(f"sync_positions_task completed successfully: {result}")
        return result
    except Exception as e:
        logger.error(f"sync_positions_task failed with error: {e}", exc_info=True)
        raise