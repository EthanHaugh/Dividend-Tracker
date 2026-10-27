from database.db import db
from database.models import (
    AccountMetadata,
    Company,
    Dividend,
    MonthlyDividends,
    YearlyDividends,
)
from flask import Blueprint, jsonify
from flask import request as flask_request
from flask_sqlalchemy.model import Model
from models.endpoints.endpoints import (
    DividendProjectionParams,
    ListAvailableTickersParams,
    ListCompanyDividendsParams,
    ListCompanyTotalsParams,
    MonthlyDividendComparisonParams,
    SortDirection,
    YearlyDividendsParams,
)
from pydantic import ValidationError
from sqlalchemy import func, or_
from sqlalchemy.orm import Query
from utils.dividend_projection import (
    calculate_average_annual_contributions,
    project_portfolio_dividends,
)

dividends_bp = Blueprint("dividends", __name__)
MONTH_LABELS = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]
MAX_COMPARISON_YEARS = 20


def _vaidate_sort_by(sort_by: str, allowed_sort_fields: str) -> bool:
    """Validate `sort_by` parameter to avoid SQL Injection"""

    return not (sort_by and sort_by not in allowed_sort_fields)


def _sort_query(
    query: Query, cls: Model, sort_by: str, sort_direction: SortDirection
) -> Query:
    if sort_direction == SortDirection.DESCENDING:
        query = query.order_by(getattr(cls, sort_by).desc())
    else:
        query = query.order_by(getattr(cls, sort_by).asc())

    return query


@dividends_bp.route("/open-positions", methods=["GET"])
def get_open_positions():
    query = db.session.query(Company).all()
    return jsonify([c.asdict() for c in query]), 200


@dividends_bp.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"}), 200


@dividends_bp.route("/yearly-dividends", methods=["GET"])
def get_yearly_dividends():
    query = db.session.query(YearlyDividends).order_by(YearlyDividends.year.asc())

    try:
        params = YearlyDividendsParams(**flask_request.args.to_dict())
    except ValidationError as e:
        return jsonify({"error": "Bad Request", "details": e.errors()}), 400

    if params.year:
        query = query.filter(YearlyDividends.year == params.year).one_or_none()
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


@dividends_bp.route("/monthly-dividends-comparison", methods=["GET"])
def get_monthly_dividends_comparison():
    data = {"years": flask_request.args.getlist("years")}

    try:
        params = MonthlyDividendComparisonParams(**data)
    except ValidationError as e:
        return jsonify({"error": "Bad Request", "details": e.errors()}), 400

    available_years_query = (
        db.session.query(MonthlyDividends.year)
        .distinct(MonthlyDividends.year)
        .order_by(MonthlyDividends.year.asc())
        .all()
    )
    available_years = [row.year for row in available_years_query]

    if not available_years:
        return jsonify({"available_years": [], "selected_years": [], "data": []}), 200

    selected_years = sorted(params.years)
    if len(params.years) == 0:
        selected_years = available_years

    if len(selected_years) > MAX_COMPARISON_YEARS:
        return (
            jsonify(
                {"error": f"A maximum of {MAX_COMPARISON_YEARS} years can be requested"}
            ),
            400,
        )

    invalid_years = [year for year in selected_years if year not in available_years]
    if invalid_years:
        return (
            jsonify(
                {
                    "error": "One or more requested years are unavailable",
                    "invalid_years": invalid_years,
                }
            ),
            400,
        )

    monthly_rows = (
        db.session.query(MonthlyDividends)
        .filter(MonthlyDividends.year.in_(selected_years))
        .all()
    )

    totals_lookup = {
        (row.year, row.month): float(row.total_dividends) for row in monthly_rows
    }

    response_data = []
    for month in range(1, 13):
        values = {
            str(year): totals_lookup.get((year, month), 0.0) for year in selected_years
        }
        response_data.append(
            {
                "month": month,
                "month_label": MONTH_LABELS[month - 1],
                "values": values,
            }
        )

    return (
        jsonify(
            {
                "available_years": available_years,
                "selected_years": selected_years,
                "data": response_data,
            }
        ),
        200,
    )


@dividends_bp.route("/account-cash", methods=["GET"])
def get_account_cash():
    account_metadata = db.session.query(AccountMetadata).one_or_none()
    if not account_metadata:
        return jsonify({"error": "No account metadata found"}), 404
    return jsonify(account_metadata.asdict()), 200


@dividends_bp.route("/pie-chart", methods=["GET"])
def get_pie_chart_data():
    """List total dividends by company for the pie chart with percentage contribution."""
    company_totals = (
        db.session.query(
            Dividend.company_id,
            Company.name,
            Company.ticker,
            func.sum(Dividend.total_payment).label("total_payment"),
        )
        .join(Company)
        .group_by(Dividend.company_id)
        .order_by(func.sum(Dividend.total_payment).desc())
    ).all()

    total_dividends = (
        sum(float(r.total_payment) for r in company_totals) if company_totals else 0
    )

    data = []
    for company_total in company_totals:
        item = company_total._asdict()
        percentage = (
            (float(company_total.total_payment) / total_dividends * 100)
            if total_dividends > 0
            else 0
        )
        item["percentage"] = round(percentage, 2)
        data.append(item)

    return (
        jsonify(
            {
                "data": data,
                "total_count": len(data),
                "total_dividends": float(total_dividends),
            }
        ),
        200,
    )


@dividends_bp.route("/list-company-totals", methods=["GET"])
def list_company_totals():
    """List total dividends for all companies with pagination"""
    params_data = flask_request.args.to_dict()
    params_data["filters"] = flask_request.args.getlist("filters") or None
    try:
        params = ListCompanyTotalsParams(**params_data)
    except ValidationError as e:
        return jsonify({"error": "Bad Request", "details": e.errors()}), 400

    allowed_sort_fields = ["name", "total_payments", "last_payment_date"]

    if not _vaidate_sort_by(params.sort_by, allowed_sort_fields):
        return jsonify(
            {"error": f"sort_by parameter must be one of: {allowed_sort_fields}"}
        ), 400

    offset = (params.page - 1) * params.page_size

    query = (
        db.session.query(
            Company.ticker,
            Company.name,
            Company.total_payments,
            func.strftime("%d-%m-%Y", func.max(Dividend.payment_date)).label(
                "last_payment_date"
            ),
        )
        .join(Dividend)
        .group_by(Company.ticker)
    )
    total_count = query.count()

    # Special handling for join and labelled column
    if params.sort_by == "last_payment_date":
        sort_column = func.max(Dividend.payment_date)
        if params.sort_direction == SortDirection.DESCENDING:
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
    else:
        query = _sort_query(query, Company, params.sort_by, params.sort_direction)

    if params.filters:
        query = query.filter(Company.ticker.in_(params.filters))
        total_count = query.count()

    if params.search:
        query = query.filter(
            or_(
                Company.ticker.ilike(f"%{params.search}%"),
                Company.name.ilike(f"%{params.search}%"),
            )
        )
        total_count = query.count()

    query = query.offset(offset).limit(params.page_size)
    return (
        jsonify(
            {
                "data": [d._asdict() for d in query],
                "page": params.page,
                "page_size": params.page_size,
                "total_count": total_count,
            }
        ),
        200,
    )


@dividends_bp.route("/list-company-dividends", methods=["GET"])
def list_company_dividends():
    """List dividends for a specific company."""

    try:
        params = ListCompanyDividendsParams(**flask_request.args.to_dict())
    except ValidationError as e:
        return jsonify({"error": "Bad Request", "details": e.errors()}), 400

    allowed_sort_fields = ["payment_date", "ticker", "total_payment"]

    if not params.ticker:
        return (
            jsonify({"error": "Missing required query string parameter: ticker"}),
            400,
        )

    if not _vaidate_sort_by(params.sort_by, allowed_sort_fields):
        return jsonify(
            {"error": f"sort_by parameter must be one of: {allowed_sort_fields}"}
        ), 400

    offset = (params.page - 1) * params.page_size

    query = (
        db.session.query(Dividend)
        .join(Company)
        .where(Dividend.company_id == Company.id)
        .filter(Company.ticker == params.ticker)
        .order_by(Dividend.payment_date.desc())
    )
    total_count = query.count()

    query = _sort_query(query, Dividend, params.sort_by, params.sort_direction)

    query = query.offset(offset).limit(params.page_size)
    return (
        jsonify(
            {
                "data": [d.asdict() for d in query.all()],
                "page": params.page,
                "page_size": params.page_size,
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

    try:
        params = ListAvailableTickersParams(**flask_request.args.to_dict())
    except ValidationError as e:
        return jsonify({"error": "Bad Request", "details": e.errors()}), 400

    query = db.session.query(Company.ticker, Company.name).distinct(Company.id)

    query = _sort_query(query, Company, "ticker", params.sort_direction)

    if not query:
        return (
            jsonify(
                {
                    "error": "Unable to retrieve available tickers, please try again later"
                }
            ),
            500,
        )

    return jsonify({"data": [company._asdict() for company in query.all()]}), 200


@dividends_bp.route("/dividend-projection", methods=["GET"])
def get_dividend_projection():
    """
    Project potential portfolio value and dividends for  years
    """

    try:
        params = DividendProjectionParams(**flask_request.args.to_dict())
    except ValidationError as e:
        return jsonify({"error": "Bad Request", "details": e.errors()}), 400

    annual_contributions = params.annual_contributions
    if not annual_contributions:
        annual_contributions = calculate_average_annual_contributions()

    return {
        "data": project_portfolio_dividends(
            annual_contribution=float(annual_contributions),
            years=params.years,
            reinvest=params.reinvest,
        ).as_dict()
    }
