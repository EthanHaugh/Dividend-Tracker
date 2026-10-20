import os

from celery.schedules import crontab
from sqlalchemy import NullPool, QueuePool


class Config:
    def __init__(self) -> None:
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False
        self.DEMO_MODE = os.environ.get("DEMO_MODE", "false").lower() == "true"

        # Assign Celery Broker to Redis
        self.CELERY_BROKER_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

        # Register re-occuring tasks
        self.CELERY_BEAT_SCHEDULE = {
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
        self.ALLOWED_ORIGINS = os.environ.get(
            "ALLOWED_ORIGINS", "http://localhost:3000"
        ).split(",")


class DevelopmentConfig(Config):
    def __init__(self) -> None:
        super().__init__()
        self.DEBUG = True
        self.BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.INSTANCE_DIR = os.path.join(self.BASE_DIR, "instance")
        os.makedirs(self.INSTANCE_DIR, exist_ok=True)

        # Assign SQL Alchemy to use the correct DB - SQL Lite for now during dev
        self.SQLALCHEMY_DATABASE_URI = (
            f"sqlite:///{os.path.join(self.INSTANCE_DIR, 'dividends.db')}"
        )
        self.SQLALCHEMY_ENGINE_OPTIONS = {"poolclass": NullPool}


class TestingConfig(Config):
    def __init__(self) -> None:
        super().__init__()
        self.TESTING = True
        self.SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
        self.SQLALCHEMY_ENGINE_OPTIONS = {"poolclass": NullPool}


class ProductionConfig(Config):
    def __init__(self) -> None:
        super().__init__()
        self.DEBUG = False
        self.TESTING = False

        self.SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "").replace(
            "postgresql://", "postgresql+psycopg://", 1
        )

        self.SQLALCHEMY_ENGINE_OPTIONS = {
            "poolclass": QueuePool,
            "pool_size": 5,
            "max_overflow": 4,
            "pool_timeout": 10,
            "pool_pre_ping": True,
            "pool_recycle": 1800,
        }

        self.PREFERRED_URL_SCHEME = "https"
        self.SESSION_COOKIE_SECURE = True
        self.SESSION_COOKIE_HTTPONLY = True
        self.SESSION_COOKIE_SAMESITE = "Lax"


config = {
    "DEVELOPMENT": DevelopmentConfig,
    "TESTING": TestingConfig,
    "PRODUCTION": ProductionConfig,
}
