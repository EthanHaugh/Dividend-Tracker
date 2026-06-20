import os
from celery.schedules import crontab
from sqlalchemy import NullPool, QueuePool


class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Assign Celery Broker to Redis
    CELERY_BROKER_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

    # Register re-occuring tasks
    CELERY_BEAT_SCHEDULE = {
        "sync-positions-once-every-5-minutes": {
            "task": "celery_service.tasks.sync_tasks.sync_positions_task",
            "schedule": crontab(minute="*/5"),
        },
        "sync-account-summary-once-every-5-minutes": {
            "task": "celery_service.tasks.sync_tasks.sync_account_summary_task",
            "schedule": crontab(minute="*/5"),
        },
        "sync-account-transactions-once-every-5-minutes": {
            "task": "celery_service.tasks.sync_tasks.sync_account_transactions_task",
            "schedule": crontab(minute="*/5"),
        },
        "sync-dividend-history-onec-per-month": {
            "task": "celery_service.tasks.sync_tasks.sync_dividend_history_task",
            "schedule": crontab(0, 0, day_of_month="1"),
        },
    }

    # CORS configuration
    ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000").split(
        ","
    )


class DevelopmentConfig(Config):
    DEBUG = True
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
    os.makedirs(INSTANCE_DIR, exist_ok=True)

    # Assign SQL Alchemy to use the correct DB - SQL Lite for now during dev
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(INSTANCE_DIR, 'dividends.db')}"
    SQLALCHEMY_ENGINE_OPTIONS = {"poolclass": NullPool}


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_ENGINE_OPTIONS = {"poolclass": NullPool}


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False

    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")

    SQLALCHEMY_ENGINE_OPTIONS = {
        "poolclass": QueuePool,
        "pool_size": 5,
        "max_overflow": 4,
        "pool_timeout": 10,
        "pool_pre_ping": True,
        "pool_recycle": 1800,
    }

    PREFERRED_URL_SCHEME = "https"
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"


config = {
    "DEVELOPMENT": DevelopmentConfig,
    "TESTING": TestingConfig,
    "PRODUCTION": ProductionConfig,
}
