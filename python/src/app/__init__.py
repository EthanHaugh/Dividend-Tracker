import logging
import os
from urllib.parse import urlparse
from flask import Flask, Config
from flask_cors import CORS
from flask_migrate import Migrate
from app.config import config
from database.db import db
from routes.endpoints import dividends_bp
from database import ensure_placeholder_company
from routes.updates import updates_bp

migrate = Migrate()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def validate_config(config: Config) -> bool:
    """Validate configuration for deployment."""

    logger.info("Validating App Configuration...")

    errors = []

    # Check database configuration
    db_uri = config["SQLALCHEMY_DATABASE_URI"]
    if not db_uri:
        errors.append("SQLALCHEMY_DATABASE_URI is not set")
    else:
        try:
            parsed = urlparse(db_uri)
            if parsed.scheme not in ["sqlite", "postgresql"]:
                errors.append(f"Unsupported database scheme: {parsed.scheme}")
        except Exception as e:
            errors.append(f"Invalid DATABASE_URL: {e}")

    celery_broker = config["CELERY_BROKER_URL"]
    if not celery_broker:
        errors.append("CELERY_BROKER_URL is not set")
    else:
        try:
            parsed = urlparse(celery_broker)
            if parsed.scheme != "redis":
                errors.append(f"Unsupported broker scheme: {parsed.scheme}")
        except Exception as e:
            errors.append(f"Invalid CELERY_BROKER_URL: {e}")

    if errors:
        raise ValueError(
            "Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
        )

    logger.info("Validated App Configuration Successfully")
    return True


def create_app(env: str | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)

    if not env:
        env = os.environ.get("FLASK_ENV", "PRODUCTION")
    app.config.from_object(config[env])

    validate_config(app.config)

    # Configure CORS with allowed origins
    allowed_origins = app.config.get("ALLOWED_ORIGINS", ["http://localhost:3000"])

    # Handle comma seperated string
    if isinstance(allowed_origins, str):
        allowed_origins = [origin.strip() for origin in allowed_origins.split(",")]

    CORS(
        app,
        resources={"/*": {"origins": allowed_origins}},
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET"],
    )

    db.init_app(app)
    migrate.init_app(app, db)

    @app.cli.command("seed-db")
    def seed_db():
        """Seed initial required data."""
        ensure_placeholder_company()
        print("Database seeded.")

    app.register_blueprint(dividends_bp)
    app.register_blueprint(updates_bp)

    from celery_service.celery_app import init_celery

    init_celery(app)

    return app
