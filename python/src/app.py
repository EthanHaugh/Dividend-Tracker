from flask import Flask
from flask_cors import CORS
from flask_executor import Executor
from routes.endpoints import dividends_bp
from routes.updates import updates_bp

app = Flask(__name__)
CORS(app)

executor = Executor()
executor.init_app(app)

app.register_blueprint(dividends_bp)
app.register_blueprint(updates_bp)

if __name__ == "__main__":
    app.run(debug=True)
