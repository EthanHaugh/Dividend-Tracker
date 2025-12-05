import time
from urllib import request
from flask import Blueprint, current_app, jsonify
from flask import request as flask_request
import requests

from consts.consts import (
    GENERATE_REPORT_URL,
    REQUEST_HEADERS,
    RETRIEVE_ACCOUNT_CASH_URL,
    RETRIEVE_OPEN_POSITIONS_URL,
    RETRIEVE_REPORT_URL,
)
from executors.executors import process_company, process_report, update_account
from models.classes import AccountCashResponse, DividendHistory
from db import Session
from models.models import DividendReport
from utils.endpoint_utils import assert_report_with_date_does_not_exist, end_of_or_today

updates_bp = Blueprint("service_updates", __name__)

""" Endpoints that retrieve data from Trading212 and update/add to SQLite DB """


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
        "timeTo": f"{end_of_or_today(year)}T00:00:00Z",
    }
    response = requests.post(GENERATE_REPORT_URL, headers=REQUEST_HEADERS, json=payload)

    if response.status_code != 200:
        return jsonify({"downloadError": response.json()}), response.status_code

    reportId = response.json().get("reportId")

    # Allow Trading 212 to process the request
    # Can't use a loop here to continue pinging T212 due to rate limiting
    time.sleep(15)

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


@updates_bp.route("/update-report", methods=["GET"])
def update_report():
    year_str = flask_request.args.get("year")
    year = int(year_str) if year_str else None
    if year is None:
        return (
            jsonify({"error": "Missing required Query String parameter: 'year'"}),
            400,
        )

    with Session() as session:
        report = (
            session.query(DividendReport)
            .filter(DividendReport.year == year)
            .one_or_none()
        )
        if not report:
            return jsonify({"error": "Report not found"}), 404

        if report.time_to.likes(year):
            pass
        session.commit()
        return jsonify({"message": "Report updated successfully"}), 200


@updates_bp.route("/update-open-positions", methods=["GET"])
def update_open_positions():
    """Fetch and update open positions in the database"""

    response = requests.get(RETRIEVE_OPEN_POSITIONS_URL, headers=REQUEST_HEADERS)
    if response.status_code != 200:
        return jsonify({"error": response.json()}), response.status_code

    current_app.extensions["executor"].submit(process_company(response.json()))

    return {"total_count": len(response.json()), "data": response.json()}


# TODO: This information needs stored in the DB and queried to avoid hitting T212 API rate limits
@updates_bp.route("/update-account-cash", methods=["GET"])
def get_account_cash():
    response = requests.get(RETRIEVE_ACCOUNT_CASH_URL, headers=REQUEST_HEADERS)
    if response.status_code != 200:
        return jsonify({"error": response.json()}), response.status_code

    current_app.extensions["executor"].submit(
        update_account(AccountCashResponse(**response.json()))
    )

    return jsonify({**response.json()}), 200
