from flask import Flask
from flask_executor import Executor
from routes.endpoints import dividends_bp

app = Flask(__name__)

executor = Executor()
executor.init_app(app)

app.register_blueprint(dividends_bp)

if __name__ == "__main__":
    app.run(debug=True)
