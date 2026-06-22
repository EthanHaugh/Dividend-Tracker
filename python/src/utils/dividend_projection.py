"""
Dividend growth rate calculation and forward projection.

GROWTH RATE METHODOLOGY
------------------------
Dividend growth is calculated on a per-share, per-company basis rather than
from total portfolio dividends. This matters because total dividends mix
two unrelated effects:
  1. Companies raising their per-share payout (real dividend growth)
  2. Buying more shares via contributions (portfolio growth, not
     dividend growth)

Per-share growth isolates effect, which is what should drive the
forward-looking growth assumption in the projection. Effect is instead
captured naturally by the projection's own reinvestment/contribution logic
- see project_portfolio_dividends() below.

Each company's first year of data is excluded from its own growth
calculation, since it likely a partial year, which would otherwise
make the following year's year-over-year figure look like an inflated
dividend "increase" that's really just ramp-up.

The final rate is the median across companies, taken per year and then
across years. Median (not mean) is used so that a small number of
structurally low-growth or dividend-cutting holdings don't dominate the
result - this answers "how is a typical holding doing" rather than
"how is my total income changing", which is a meaningfully different
question (total income growth is also affected by position sizing and
contributions).
"""

import statistics
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, timedelta

from database import db
from database.models import (
    AccountMetadata,
    AccountTransactions,
    Dividend,
    TransactionType,
)


@dataclass
class GrowthRateResult:
    """Diagnostics behind the calculated dividend growth rate."""

    rate: float  # decimal fraction, e.g. 0.029 for 2.9%
    companies_used: int
    years_used: list[int]
    yearly_medians: dict[int, float] = field(default_factory=dict)


@dataclass
class ProjectionYear:
    year: int
    portfolio_value: float
    annual_dividend: float
    yield_on_cost: float  # annual_dividend / original portfolio value
    cumulative_contributions: float  # total contributed up to and including this year
    real_portfolio_value: float  # inflation-adjusted to today's money
    real_annual_dividend: float  # inflation-adjusted to today's money


@dataclass
class DividendProjection:
    """Everything a dashboard needs to render a dividend growth projection."""

    growth_rate: float
    growth_rate_companies_used: int
    capital_growth_rate: float
    inflation_rate: float
    starting_portfolio_value: float
    starting_yield: float
    annual_contribution: float
    reinvest: bool
    years: list[ProjectionYear]

    @property
    def final_year(self) -> ProjectionYear:
        return self.years[-1]

    @property
    def total_dividend_growth_pct(self) -> float:
        """Total % increase in annual dividend from year 1 to the final year."""
        first, last = self.years[0].annual_dividend, self.years[-1].annual_dividend
        if first <= 0:
            return 0.0
        return (last - first) / first

    @property
    def total_contributions(self) -> float:
        """Total amount contributed over the whole projection period."""
        return self.final_year.cumulative_contributions

    @property
    def investment_only_growth(self) -> float:
        """
        How much the final portfolio value grew from investment performance
        alone (capital growth + dividends), excluding money you simply
        added via contributions. This is the figure that answers "did
        investing actually work", separate from "I also just put more
        money in".
        """
        return (
            self.final_year.portfolio_value
            - self.starting_portfolio_value
            - self.total_contributions
        )

    @property
    def cagr(self) -> float:
        """
        Compound annual growth rate of portfolio value over the projection
        period, as a decimal fraction. This is a BLENDED output figure
        reflecting capital growth + dividend reinvestment + contribution
        timing all together - distinct from capital_growth_rate, which is
        an input assumption about price appreciation alone.

        NOTE: since contributions are added throughout the period, this
        is not a pure "return on initial capital" figure - it's the
        annualized growth rate of total value, including new money added.
        For a cleaner read on investment performance alone, use
        investment_only_growth instead.
        """
        years_elapsed = len(self.years)
        if years_elapsed == 0 or self.starting_portfolio_value <= 0:
            return 0.0
        ratio = self.final_year.portfolio_value / self.starting_portfolio_value
        if ratio <= 0:
            return 0.0
        return ratio ** (1 / years_elapsed) - 1

    @property
    def cumulative_dividends_received(self) -> float:
        """Total dividend income received across the entire projection period."""
        return sum(y.annual_dividend for y in self.years)

    @property
    def years_until_dividends_cover_contribution(self) -> int | None:
        """
        The first year in which annual_dividend >= annual_contribution -
        i.e. when your dividend income alone could fund your next year's
        contribution. Returns None if this never happens within the
        projected period, or if annual_contribution is 0 (the milestone
        isn't meaningful without a contribution to compare against).
        """
        if self.annual_contribution <= 0:
            return None
        for y in self.years:
            if y.annual_dividend >= self.annual_contribution:
                return y.year
        return None

    def as_dict(self) -> dict:
        return {
            "growth_rate": round(self.growth_rate, 4),
            "growth_rate_pct": f"{self.growth_rate:.2%}",
            "growth_rate_companies_used": self.growth_rate_companies_used,
            "capital_growth_rate": round(self.capital_growth_rate, 4),
            "capital_growth_rate_pct": f"{self.capital_growth_rate:.2%}",
            "inflation_rate": round(self.inflation_rate, 4),
            "inflation_rate_pct": f"{self.inflation_rate:.2%}",
            "starting_portfolio_value": round(self.starting_portfolio_value, 2),
            "starting_yield_pct": f"{self.starting_yield:.2%}",
            "annual_contribution": round(self.annual_contribution, 2),
            "reinvest": self.reinvest,
            "total_dividend_growth_pct": f"{self.total_dividend_growth_pct:.1%}",
            "total_contributions": round(self.total_contributions, 2),
            "investment_only_growth": round(self.investment_only_growth, 2),
            "cagr": round(self.cagr, 4),
            "cagr_pct": f"{self.cagr:.2%}",
            "cumulative_dividends_received": round(
                self.cumulative_dividends_received, 2
            ),
            "years_until_dividends_cover_contribution": self.years_until_dividends_cover_contribution,
            "final_year": {
                "year": self.final_year.year,
                "portfolio_value": round(self.final_year.portfolio_value, 2),
                "annual_dividend": round(self.final_year.annual_dividend, 2),
                "real_portfolio_value": round(self.final_year.real_portfolio_value, 2),
                "real_annual_dividend": round(self.final_year.real_annual_dividend, 2),
            },
            "years": [
                {
                    "year": y.year,
                    "portfolio_value": round(y.portfolio_value, 2),
                    "annual_dividend": round(y.annual_dividend, 2),
                    "yield_on_cost_pct": f"{y.yield_on_cost:.2%}",
                    "cumulative_contributions": round(y.cumulative_contributions, 2),
                    "real_portfolio_value": round(y.real_portfolio_value, 2),
                    "real_annual_dividend": round(y.real_annual_dividend, 2),
                }
                for y in self.years
            ],
        }


def _xnpv(rate: float, cash_flows: list[tuple[date, float]], as_of: date) -> float:
    """
    Net value of dated cash flows, each compounded FORWARD to `as_of` at
    the given annual rate. The root of this function (as a function of
    rate) is the annualized rate that reconciles the cash flows with the
    final value - i.e. the money-weighted return (XIRR).
    """
    return sum(
        amount * (1 + rate) ** ((as_of - d).days / 365.0) for d, amount in cash_flows
    )


def _solve_xirr(
    cash_flows: list[tuple[date, float]], as_of: date, guess: float = 0.08
) -> float:
    """
    Solves for the rate where _xnpv(rate, cash_flows, as_of) == 0, using
    Newton's method with a bisection fallback for robustness.

    Returns the guess unchanged if a root can't be found (e.g. too little
    data, or all cash flows on the same side of zero).
    """
    rate = guess
    for _ in range(100):
        npv = _xnpv(rate, cash_flows, as_of)
        d_rate = 1e-6
        derivative = (_xnpv(rate + d_rate, cash_flows, as_of) - npv) / d_rate
        if abs(derivative) < 1e-12:
            break
        new_rate = rate - npv / derivative
        if abs(new_rate - rate) < 1e-8:
            return new_rate
        rate = new_rate

    # Newton's method didn't converge cleanly - fall back to bisection
    # over a wide, sane range for an investment return.
    lo, hi = -0.99, 10.0
    f_lo, f_hi = _xnpv(lo, cash_flows, as_of), _xnpv(hi, cash_flows, as_of)
    if f_lo * f_hi > 0:
        return rate  # can't bracket a root - return best Newton estimate
    for _ in range(200):
        mid = (lo + hi) / 2
        f_mid = _xnpv(mid, cash_flows, as_of)
        if abs(f_mid) < 1e-6:
            return mid
        if f_lo * f_mid < 0:
            hi = mid
        else:
            lo, f_lo = mid, f_mid
    return (lo + hi) / 2


def calculate_capital_growth_rate(
    current_portfolio_value: float | None = None,
) -> float:
    """
    Estimates the portfolio's annualized capital growth rate (price
    appreciation only, excluding dividends), as a decimal fraction
    (e.g. 0.07 for 7%).

    Method (money-weighted return / XIRR):
      1. Treat every historical deposit as a negative cash flow on the
         date it happened.
      2. Treat the current portfolio value as a final positive cash flow
         today, MINUS total dividends received historically - dividends
         represent income already captured elsewhere (see
         calculate_dividend_growth_rate / calculate_current_yield), so
         they're backed out here to avoid double-counting their
         contribution to the portfolio's growth.
      3. Solve for the single annual rate that reconciles these cash
         flows with that adjusted value.

    This requires no historical value snapshots - only the dated deposit
    history and the current value - which is what we have available.

    Returns 0.0 if there isn't enough deposit history to calculate a rate.
    """
    if current_portfolio_value is None:
        current_portfolio_value = get_current_portfolio_value()

    if current_portfolio_value <= 0:
        return 0.0

    deposits = (
        db.session.query(AccountTransactions)
        .filter(AccountTransactions.transaction_type == TransactionType.DEPOSIT)
        .all()
    )
    if not deposits:
        return 0.0

    today = date.today()
    cash_flows = [
        (d.transaction_date.date(), -float(d.transaction_amount)) for d in deposits
    ]

    total_dividends = sum(
        float(d.total_payment) for d in db.session.query(Dividend).all()
    )
    value_excl_dividends = current_portfolio_value - total_dividends

    cash_flows.append((today, value_excl_dividends))

    return _solve_xirr(cash_flows, today)


def calculate_dividend_growth_rate(
    exclude_current_year: bool = True,
) -> GrowthRateResult:
    """
    Calculates the median per-share dividend growth rate across all
    companies with enough history to measure (3+ years of data).

    Returns a GrowthRateResult with the rate as a decimal fraction
    (e.g. 0.029 for 2.9%), plus diagnostics for display/debugging.
    """
    dividends = db.session.query(Dividend).all()
    if not dividends:
        return GrowthRateResult(rate=0.0, companies_used=0, years_used=[])

    current_year = date.today().year

    dps_by_company_year: dict[int, dict[int, float]] = defaultdict(
        lambda: defaultdict(float)
    )
    for d in dividends:
        if exclude_current_year and d.year >= current_year:
            # Current year is likely incomplete - comparing a partial
            # year against a prior full year would be misleading.
            continue
        if d.number_of_shares <= 0:
            continue
        dps = float(d.total_payment) / d.number_of_shares
        dps_by_company_year[d.company_id][d.year] += dps

    growth_by_year: dict[int, list[float]] = defaultdict(list)
    companies_used = 0

    for company_id, year_dps in dps_by_company_year.items():
        years = sorted(year_dps.keys())
        if len(years) < 3:
            # not enough history for a reliable transition
            continue
        companies_used += 1

        # Skip the first transition, a company's first year
        # of data is often partial/position opened mid-year
        for i in range(2, len(years)):
            prev_year, curr_year = years[i - 1], years[i]
            prev_dps, curr_dps = year_dps[prev_year], year_dps[curr_year]
            if prev_dps <= 0:
                continue
            growth_by_year[curr_year].append((curr_dps - prev_dps) / prev_dps)

    if not growth_by_year:
        return GrowthRateResult(rate=0.0, companies_used=0, years_used=[])

    yearly_medians = {
        year: statistics.median(rates) for year, rates in growth_by_year.items()
    }
    overall_rate = statistics.median(yearly_medians.values())

    return GrowthRateResult(
        rate=overall_rate,
        companies_used=companies_used,
        years_used=sorted(yearly_medians.keys()),
        yearly_medians=yearly_medians,
    )


def get_current_portfolio_value() -> float:
    """
    Reads the current account value from AccountMetadata.

    Returns 0.0 if no account metadata row exists, or if the stored value
    is not positive.
    """
    account = db.session.query(AccountMetadata).first()
    if account is None or account.account_value <= 0:
        return 0.0
    return float(account.account_value)


def calculate_current_yield(portfolio_value: float | None = None) -> float:
    """
    Calculates current portfolio yield as trailing-12-month (TTM) dividends
    received, divided by current portfolio value.

    TTM is used rather than last-calendar-year, so the figure
    stays current year-round rather than going stale for
    months after a calendar year ends.

    If portfolio_value is not provided, it's read via get_current_portfolio_value().
    Returns 0.0 if there's no dividend history or no portfolio value
    available.
    """
    if portfolio_value is None:
        portfolio_value = get_current_portfolio_value()

    if portfolio_value <= 0:
        return 0.0

    cutoff_date = date.today() - timedelta(days=365)

    ttm_dividends = (
        db.session.query(Dividend).filter(Dividend.payment_date >= cutoff_date).all()
    )

    total_ttm = sum(float(d.total_payment) for d in ttm_dividends)

    return total_ttm / portfolio_value


def calculate_average_annual_contributions() -> float:
    """
    Calculates the average annual contribution amount, based on total
    contributions (DEPOSIT and TRANSFER transactions) divided by the
    number of years since the first contribution (inclusive of the
    current, possibly partial, year).

    This intentionally divides by calendar span rather than "number of
    years with a contribution" - a year with no contributions should pull
    the average down, not be excluded, since the goal is "what's my
    actual average pace of contributing", not "what do I contribute in a
    typical active year".

    Returns 0.0 if there are no contributions on record.
    """
    contributions = (
        db.session.query(AccountTransactions)
        .filter(
            AccountTransactions.transaction_type.in_(
                [TransactionType.DEPOSIT, TransactionType.TRANSFER]
            )
        )
        .filter(AccountTransactions.transaction_amount >= 0)
        .all()
    )
    if not contributions:
        return 0.0

    total_contributed = sum(float(c.transaction_amount) for c in contributions)

    first_contribution_date = min(c.transaction_date.date() for c in contributions)
    years_span = (date.today() - first_contribution_date).days / 365.0

    if years_span <= 0:
        # All contributions happened today / first contribution is today -
        # can't annualize a zero-length span, so just return the total as-is.
        return total_contributed

    return total_contributed / years_span


def project_portfolio_dividends(
    current_portfolio_value: float | None = None,
    current_yield: float | None = None,
    annual_contribution: float = 0.0,
    years: int = 10,
    dividend_growth_rate: float | None = None,
    capital_growth_rate: float | None = None,
    inflation_rate: float = 0.03,  # Worldwide aver. is 3% a year
    reinvest: bool = True,
) -> DividendProjection:
    """
    Projects portfolio value and annual dividend income.

    Each year:
      - annual_dividend = portfolio_value * yield_rate (at start of year)
      - portfolio_value grows by: the dividend (if reinvested), the
        annual contribution, AND capital_growth_rate (price appreciation,
        independent of dividends/contributions)
      - yield_rate compounds by dividend_growth_rate, modeling rising
        yield-on-cost as the underlying companies raise their payouts

    Without capital_growth_rate, the projection only reflects dividends
    and contributions - which understates real-world portfolio growth,
    since share price appreciation is usually the dominant driver of
    portfolio value over time. Pass 0.0 explicitly if you want the old
    contributions-and-dividends-only behavior.

    If current_portfolio_value is not provided, it is read automatically
    via get_current_portfolio_value().

    If dividend_growth_rate is not provided, it is calculated automatically
    from historical per-share dividend data via calculate_dividend_growth_rate().

    If current_yield is not provided, it is calculated automatically as
    trailing-12-month dividends / current_portfolio_value via
    calculate_current_yield().

    If capital_growth_rate is not provided, it is calculated automatically
    from historical deposits and current value via
    calculate_capital_growth_rate(). NOTE: unlike dividend growth (which
    has a real causal anchor in company payout policy), future price
    growth is fundamentally not predictable from history the same way -
    markets move in multi-year cycles that don't repeat on schedule. This
    default is a reasonable starting point, not a forecast - consider
    letting users override it in the dashboard.

    inflation_rate is used only to compute real_portfolio_value and
    real_annual_dividend on each ProjectionYear (today's-money
    equivalents), and defaults to a flat 2.5% assumption. It does not
    affect the nominal projection math at all.
    """
    if current_portfolio_value is None:
        current_portfolio_value = get_current_portfolio_value()

    if current_yield is None:
        current_yield = calculate_current_yield(portfolio_value=current_portfolio_value)

    growth_result = None
    if dividend_growth_rate is None:
        growth_result = calculate_dividend_growth_rate()
        dividend_growth_rate = growth_result.rate

    if capital_growth_rate is None:
        capital_growth_rate = calculate_capital_growth_rate(
            current_portfolio_value=current_portfolio_value
        )

    portfolio_value = current_portfolio_value
    yield_rate = current_yield
    cumulative_contributions = 0.0
    projection_years: list[ProjectionYear] = []

    for year in range(1, years + 1):
        annual_dividend = portfolio_value * yield_rate

        if reinvest:
            portfolio_value += annual_dividend
        portfolio_value += annual_contribution
        cumulative_contributions += annual_contribution
        portfolio_value *= 1 + capital_growth_rate

        yield_rate *= 1 + dividend_growth_rate

        inflation_factor = (1 + inflation_rate) ** year

        projection_years.append(
            ProjectionYear(
                year=year,
                portfolio_value=portfolio_value,
                annual_dividend=annual_dividend,
                yield_on_cost=(
                    annual_dividend / current_portfolio_value
                    if current_portfolio_value > 0
                    else 0.0
                ),
                cumulative_contributions=cumulative_contributions,
                real_portfolio_value=portfolio_value / inflation_factor,
                real_annual_dividend=annual_dividend / inflation_factor,
            )
        )

    return DividendProjection(
        growth_rate=dividend_growth_rate,
        growth_rate_companies_used=growth_result.companies_used if growth_result else 0,
        capital_growth_rate=capital_growth_rate,
        inflation_rate=inflation_rate,
        starting_portfolio_value=current_portfolio_value,
        starting_yield=current_yield,
        annual_contribution=annual_contribution,
        reinvest=reinvest,
        years=projection_years,
    )


if __name__ == "__main__":
    import json

    from flask import Flask

    from app.config import config

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config["DEVELOPMENT"])
    db.init_app(app)

    with app.app_context():
        projection = project_portfolio_dividends(
            annual_contribution=10000,
            years=10,
        )
        print(json.dumps(projection.as_dict(), indent=2))

        print("\n--- simple list[dict] version ---")
        simple = project_portfolio_dividends(
            annual_contribution=10000,
            years=10,
        )
        print(json.dumps(simple, indent=2))
