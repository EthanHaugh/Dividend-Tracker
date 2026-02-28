import logging

from flask import Blueprint, jsonify
from flask import request as flask_request
from tasks.sync_tasks import sync_dividend_history_task

updates_bp = Blueprint("service_updates", __name__)
logger = logging.Logger(__name__)

@updates_bp.route("/download", methods=["GET"])
def get_dividend_history():
    """Request Trading 212 to make a new Report and Download it"""

    year_str = flask_request.args.get("year")
    year = int(year_str) if year_str else None

    if year is None:
        return (
            jsonify({"error": "Missing required Query String parameter: 'year'"}),
            400,
        )

    logger.info(f"On-demand dividend history download requested for year {year}")

    task = sync_dividend_history_task.delay(year)

    return jsonify(
        {
            "status": "processing",
            "message": f"Dividend history download started for year {year}",
            "task_id": task.id,
        }
    ), 202 
