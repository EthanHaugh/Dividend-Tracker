from enum import Enum
from flask import Blueprint, jsonify
from flask import request as flask_request
from sqlalchemy import func
from sqlalchemy.orm import Query

from app import db
from models.models import AccountMetadata, Company, Dividend, YearlyDividends

dividends_bp = Blueprint("dividends", __name__)


# Default type for sort_direction, if a passed value is not of type SortDirection
# the flask_request.args.get() with return the default value
class SortDirection(Enum):
    ASCENDING = "asc"
    DESCENDING = "desc"


def _vaidate_sort_by(sort_by: str, allowed_sort_fields: str) -> bool:
    """Validate `sort_by` parameter to avoid SQL Injection"""

    if sort_by:
        # Avoid SQL Injection
        if sort_by not in allowed_sort_fields:
            return False

    return True


def _sort_query(query: Query, sort_by: str, sort_direction: SortDirection) -> Query:
    if sort_direction == SortDirection.DESCENDING:
        query = query.order_by(getattr(Dividend, sort_by).desc())
    else:
        query = query.order_by(getattr(Dividend, sort_by).asc())

    return query


@dividends_bp.route("/open-positions", methods=["GET"])
def get_open_positions():
    query = db.session.query(Company).all()
    return jsonify([c.asdict() for c in query]), 200


@dividends_bp.route("/yearly-dividends", methods=["GET"])
def get_yearly_dividends():
    query = db.session.query(YearlyDividends).order_by(YearlyDividends.year.asc())

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
    total = db.session.query(func.sum(YearlyDividends.total_dividends)).scalar() or 0
    return jsonify({"total_dividends": float(total)}), 200


@dividends_bp.route("/account-cash", methods=["GET"])
def get_account_cash():
    account_metadata = db.session.query(AccountMetadata).one_or_none()
    if not account_metadata:
        return jsonify({"error": "No account metadata found"}), 404
    return jsonify(account_metadata.asdict()), 200


@dividends_bp.route("/pie-chart", methods=["GET"])
def get_pie_chart_data():
    """List total dividends by company for the pie chart."""
    query = (
        db.session.query(
            Dividend.ticker, func.sum(Dividend.total_payment).label("total_payment")
        )
        .group_by(Dividend.ticker)
        .order_by(func.sum(Dividend.total_payment).desc())
        .all()
    )
    return (
        jsonify({"data": [d._asdict() for d in query]}),
        200,
    )


@dividends_bp.route("/list-company-totals", methods=["GET"])
def list_company_totals():
    """List total dividends for all companies with pagination"""
    page = flask_request.args.get("page", default=1, type=int)
    page_size = flask_request.args.get("page_size", default=10, type=int)
    search = flask_request.args.get("search", default=None, type=str)
    filters = flask_request.args.get("filters", default=None, type=str)
    sort_by = flask_request.args.get("sort_by", default="ticker", type=str)
    sort_direction = flask_request.args.get(
        "sort_direction", default=SortDirection.DESCENDING, type=SortDirection
    )

    allowed_sort_fields = ["ticker", "total_payment"]

    if not _vaidate_sort_by(sort_by, allowed_sort_fields):
        return jsonify(
            {"error": f"sort_by parameter must be one of: {allowed_sort_fields}"}
        ), 400

    if filters:
        filters = filters.split(",")

    offset = (page - 1) * page_size

    query = db.session.query(
        Dividend.ticker, func.sum(Dividend.total_payment).label("total_payment")
    ).group_by(Dividend.ticker)
    total_count = query.count()

    query = _sort_query(query, sort_by, sort_direction)

    if filters:
        query = query.filter(Dividend.ticker.in_(filters))

    if search:
        query = query.filter(Dividend.ticker.ilike(f"%{search}%"))

    query = query.offset(offset).limit(page_size)
    return (
        jsonify(
            {
                "data": [d._asdict() for d in query],
                "page": page,
                "page_size": page_size,
                "total_count": total_count,
            }
        ),
        200,
    )


@dividends_bp.route("/list-company-dividends", methods=["GET"])
def list_company_dividends():
    """List dividends for a specific company."""
    page = flask_request.args.get("page", default=1, type=int)
    page_size = flask_request.args.get("page_size", default=10, type=int)
    ticker = flask_request.args.get("ticker", default=None, type=str)
    sort_by = flask_request.args.get("sort_by", default="payment_date", type=str)
    sort_direction = flask_request.args.get(
        "sort_direction", default=SortDirection.ASCENDING, type=SortDirection
    )
    allowed_sort_fields = ["payment_date", "ticker", "total_payment"]

    if not ticker:
        return (
            jsonify({"error": "Query string parameter, ticker, is required"}),
            400,
        )

    if not _vaidate_sort_by(sort_by, allowed_sort_fields):
        return jsonify(
            {"error": f"sort_by parameter must be one of: {allowed_sort_fields}"}
        ), 400

    offset = (page - 1) * page_size

    query = db.session.query(Dividend).filter(Dividend.ticker == ticker)
    total_count = query.count()

    query = _sort_query(query, sort_by, sort_direction)

    query = query.offset(offset).limit(page_size)
    return (
        jsonify(
            {
                "data": [d.asdict() for d in query],
                "page": page,
                "page_size": page_size,
                "total_count": total_count,
            }
        ),
        200,
    )


@dividends_bp.route("/list-available-tickers", methods=["GET"])
def get_available_tickers():
    """
    Fetch available tickers to sort on, use the Dividends table
    to be in line with the `list_company_totals` endpoint
    """
    sort_direction = flask_request.args.get(
        "sort_direction", default=SortDirection.ASCENDING, type=SortDirection
    )
    query = db.session.query(Dividend.ticker).distinct(Dividend.ticker)

    query = _sort_query(query, "ticker", sort_direction)

    if not query:
        return (
            jsonify(
                {
                    "error": "Unable to retrieve available tickers, please try again later"
                }
            ),
            500,
        )

    return jsonify({"data": [ticker.ticker for ticker in query.all()]}), 200
