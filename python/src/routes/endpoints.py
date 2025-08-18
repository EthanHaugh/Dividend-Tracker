from flask import Blueprint, jsonify, current_app
import time
from flask import request as flask_request
from executors.executors import process_company, process_report
import requests
from urllib import request

from models.classes import DividendHistory
from consts.consts import (
    GENERATE_REPORT_URL,
    REQUEST_HEADERS,
    RETRIEVE_OPEN_POSITIONS_URL,
    RETRIEVE_REPORT_URL,
)
from db import Session
from models.models import YearlyDividends
from utils.endpoint_utils import assert_report_with_date_does_not_exist

dividends_bp = Blueprint("dividends", __name__)


@dividends_bp.route("/download", methods=["GET"])
def get_dividend_history():
    """Request Trading 212 to make a new Report and Download it"""

    year_str = flask_request.args.get("year")
    year = int(year_str) if year_str else None
    if year is None:
        return (
            jsonify({"error": "Missing required Query String parameter: 'year'"}),
            400,
        )

    if assert_report_with_date_does_not_exist(year):
        return jsonify({"error": "Report for the specified year already exists"}), 400

    payload = {
        "dataIncluded": {
            "includeDividends": True,
            "includeInterest": False,
            "includeOrders": False,
            "includeTransactions": False,
        },
        "timeFrom": f"{year}-01-01T00:00:00Z",
        "timeTo": f"{year + 1}-01-01T00:00:00Z",
    }
    response = requests.post(GENERATE_REPORT_URL, headers=REQUEST_HEADERS, json=payload)

    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch data"}), response.status_code

    reportId = response.json().get("reportId")

    # Allow Trading 212 to process the request
    time.sleep(6)

    # Download report from Trading 212 using above response ID
    response = requests.get(RETRIEVE_REPORT_URL, headers=REQUEST_HEADERS)
    if response.status_code != 200:
        return jsonify({"error": response.json()}), response.status_code

    # Iterate through response to find correct report
    for item in response.json():
        if item["reportId"] == int(reportId):
            dividend_history = DividendHistory(
                reportId=item["reportId"],
                downloadLink=item["downloadLink"],
                timeFrom=item["timeFrom"],
                timeTo=item["timeTo"],
            )
            request.urlretrieve(item["downloadLink"], "downloaded.csv")
            current_app.extensions["executor"].submit(
                process_report(dividend_history, year)
            )

            return jsonify(item), 200

    return jsonify({"error": f"Report with ID: {reportId} does not exist"}), 404


@dividends_bp.route("/open-positions", methods=["GET"])
def get_open_positions():
    """Fetch all open positions from Trading 212 and store them in the database"""

    response = requests.get(RETRIEVE_OPEN_POSITIONS_URL, headers=REQUEST_HEADERS)
    if response.status_code != 200:
        return jsonify({"error": response.json()}), response.status_code

    current_app.extensions["executor"].submit(process_company(response.json()))

    return {"total_count": len(response.json()), "data": response.json()}


@dividends_bp.route("/yearly-dividends", methods=["GET"])
def get_yearly_dividends():
    with Session() as session:
        yearly_dividends = (
            session.query(YearlyDividends).order_by(YearlyDividends.year.desc()).all()
        )
        return jsonify([yd.asdict() for yd in yearly_dividends]), 200
