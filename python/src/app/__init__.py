import logging
import os
from urllib.parse import urlparse

from database import ensure_placeholder_company
from database.db import db
from flask import Config, Flask, send_from_directory
from flask_cors import CORS
from flask_migrate import Migrate
from routes.endpoints import dividends_bp
from routes.updates import updates_bp

from app.config import config

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
            if parsed.scheme not in ["sqlite", "postgresql", "postgresql+psycopg"]:
                errors.append(f"Unsupported database scheme: {parsed.scheme}")
        except ValueError as e:
            errors.append(f"Invalid DATABASE_URL: {e}")

    if not config["DEMO_MODE"]:
        celery_broker = config["CELERY_BROKER_URL"]
        if not celery_broker:
            errors.append("CELERY_BROKER_URL is not set")
        else:
            try:
                parsed = urlparse(celery_broker)
                if parsed.scheme != "redis":
                    errors.append(f"Unsupported broker scheme: {parsed.scheme}")
            except ValueError as e:
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
    app.config["DEMO_MODE"] = os.environ.get("DEMO_MODE", "false").lower() == "true"

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

    @app.cli.command("seed-demo")
    def seed_demo():
        """Seed deterministic synthetic data for the public demo."""
        if not app.config["DEMO_MODE"]:
            raise RuntimeError("seed-demo requires DEMO_MODE=true")

        from database.demo_seed import seed_demo_data

        seed_demo_data()
        print("Demo data seeded.")

    app.register_blueprint(dividends_bp)

    if app.config["DEMO_MODE"]:
        frontend_dir = app.static_folder
        if frontend_dir is not None:
            app.config["DEMO_FRONTEND_DIR"] = frontend_dir
            app.static_folder = os.path.join(frontend_dir, "static")

        @app.route("/", defaults={"path": ""})
        @app.route("/<path:path>")
        def serve_demo(path: str):
            """Serve the compiled React application in the demo container."""
            if path == "download":
                return {"error": "Not found"}, 404

            frontend_dir = app.config.get("DEMO_FRONTEND_DIR")
            if frontend_dir is None:
                return {"error": "Demo frontend is not available"}, 404

            index_path = os.path.join(frontend_dir, "index.html")
            requested_path = os.path.join(frontend_dir, path)
            if path and os.path.isfile(requested_path):
                return send_from_directory(frontend_dir, path)
            if os.path.isfile(index_path):
                return send_from_directory(frontend_dir, "index.html")
            return {"error": "Demo frontend is not available"}, 404
    else:
        app.register_blueprint(updates_bp)

        from celery_service.celery_app import init_celery

        init_celery(app)

    return app
