import os
from celery.schedules import crontab

class Config:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
    
    # Ensure instance directory exists
    os.makedirs(INSTANCE_DIR, exist_ok=True)
    
    # Assign SQL Alchemy to use the correct DB - SQL Lite for now during dev
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(INSTANCE_DIR, 'dividends.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Assign Celery Broker to Redis
    CELERY_BROKER_URL = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND = "redis://localhost:6379/0"

    # Register re-occuring tasks
    CELERY_BEAT_SCHEDULE = {
        'sync-positions-once-every-5-minutes': {
            'task': 'tasks.sync_tasks.sync_positions_task',
            'schedule': crontab(minute='*/5')
        },
        'sync-account-summary-once-every-5-minutes': {
            'task': 'tasks.sync_tasks.sync_account_summary_task',
            'schedule': crontab(minute='*/5')
        },
        'sync-dividend-history-onec-per-month': {
            'task': 'tasks.sync_tasks.sync_dividend_history_task',
            'schedule': crontab(0, 0, day_of_month='1')
        }
    }