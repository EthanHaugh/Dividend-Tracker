from flask import Blueprint, jsonify
from flask import request as flask_request
import requests
from sqlalchemy import func

from consts.consts import (
    REQUEST_HEADERS,
    RETRIEVE_ACCOUNT_CASH_URL,
)
from db import Session
from models.models import AccountMetadata, Company, YearlyDividends

dividends_bp = Blueprint("dividends", __name__)


@dividends_bp.route("/open-positions", methods=["GET"])
def get_open_positions():
    with Session() as session:
        query = session.query(Company).all()
        return jsonify([c.asdict() for c in query]), 200


@dividends_bp.route("/yearly-dividends", methods=["GET"])
def get_yearly_dividends():
    with Session() as session:
        query = session.query(YearlyDividends).order_by(YearlyDividends.year.desc())

        year_str = flask_request.args.get("year")
        year = int(year_str) if year_str else None
        if year:
            query = query.filter(YearlyDividends.year == year).one_or_none()
            if not query:
                return jsonify({"error": "No yearly dividends found"}), 404
            return (
                [query.asdict()],
                200,
            )

        return jsonify([yd.asdict() for yd in query.all()]), 200


@dividends_bp.route("/total-dividends", methods=["GET"])
def get_total_dividends():
    with Session() as session:
        total = session.query(func.sum(YearlyDividends.total_dividends)).scalar() or 0
        return jsonify({"total_dividends": float(total)}), 200


# TODO: This information needs stored in the DB and queried to avoid hitting T212 API rate limits
@dividends_bp.route("/account-cash", methods=["GET"])
def get_account_cash():
    with Session() as session:
        account_metadata = session.query(AccountMetadata).one_or_none()
        if not account_metadata:
            return jsonify({"error": "No account metadata found"}), 404
        return jsonify(account_metadata.asdict()), 200
