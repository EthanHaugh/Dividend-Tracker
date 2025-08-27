from flask import Blueprint, jsonify
from flask import request as flask_request
from sqlalchemy import func

from db import Session
from models.models import AccountMetadata, Company, Dividend, YearlyDividends

dividends_bp = Blueprint("dividends", __name__)


@dividends_bp.route("/open-positions", methods=["GET"])
def get_open_positions():
    with Session() as session:
        query = session.query(Company).all()
        return jsonify([c.asdict() for c in query]), 200


@dividends_bp.route("/yearly-dividends", methods=["GET"])
def get_yearly_dividends():
    with Session() as session:
        query = session.query(YearlyDividends).order_by(YearlyDividends.year.asc())

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


@dividends_bp.route("/account-cash", methods=["GET"])
def get_account_cash():
    with Session() as session:
        account_metadata = session.query(AccountMetadata).one_or_none()
        if not account_metadata:
            return jsonify({"error": "No account metadata found"}), 404
        return jsonify(account_metadata.asdict()), 200


@dividends_bp.route("/pie-chart", methods=["GET"])
def get_pie_chart_data():
    """List total dividends by company for the pie chart."""
    with Session() as session:
        query = (
            session.query(
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
    with Session() as session:
        page = flask_request.args.get("page", default=1, type=int)
        page_size = flask_request.args.get("page_size", default=10, type=int)
        search = flask_request.args.get("search", default=None, type=str)

        offset = (page - 1) * page_size

        query = (
            session.query(
                Dividend.ticker, func.sum(Dividend.total_payment).label("total_payment")
            )
            .group_by(Dividend.ticker)
            .order_by(func.sum(Dividend.total_payment).desc())
        )
        total_count = query.count()

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
    with Session() as session:
        page = flask_request.args.get("page", default=1, type=int)
        page_size = flask_request.args.get("page_size", default=10, type=int)
        ticker = flask_request.args.get("ticker", default=None, type=str)

        if not ticker:
            return (
                jsonify({"error": "Query string parameter, ticker, is required"}),
                400,
            )

        offset = (page - 1) * page_size

        query = (
            session.query(Dividend)
            .filter(Dividend.ticker == ticker)
            .order_by(Dividend.payment_date.desc())
        )
        total_count = query.count()

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
