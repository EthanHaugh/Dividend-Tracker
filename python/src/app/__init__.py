from flask import Flask
from flask_cors import CORS
from flask_executor import Executor
from flask_migrate import Migrate
from app.config import Config
from app.db import db
from routes.endpoints import dividends_bp
from routes.updates import updates_bp
import models  # noqa: F401

executor = Executor()
migrate = Migrate()

def create_app() -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    CORS(app)

    db.init_app(app)
    migrate.init_app(app, db)
    executor.init_app(app)

    app.register_blueprint(dividends_bp)
    app.register_blueprint(updates_bp)

    from celery_app import init_celery
    init_celery(app)

    return app