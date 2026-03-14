import os
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from app.config import config
from database.db import db
from routes.endpoints import dividends_bp
from database import ensure_placeholder_company
from routes.updates import updates_bp

migrate = Migrate()


def create_app() -> Flask:
    app = Flask(__name__, instance_relative_config=True)

    env = os.environ.get("FLASK_ENV", "PRODUCTION")
    app.config.from_object(config[env])

    CORS(app)

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
