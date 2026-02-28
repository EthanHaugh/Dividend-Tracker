from flask import Flask
from flask_cors import CORS
from flask_executor import Executor
from flask_migrate import Migrate
from routes.endpoints import dividends_bp
from db import db
from routes.updates import updates_bp
import models

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///dividends.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

executor = Executor()
executor.init_app(app)

db.init_app(app)
migrate = Migrate(app, db)

app.register_blueprint(dividends_bp)
app.register_blueprint(updates_bp)

if __name__ == "__main__":
    app.run(debug=True)
