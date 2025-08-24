from db import Session
from sqlalchemy import extract
from models.models import DividendReport
from datetime import date


def assert_report_with_date_does_not_exist(year: int) -> bool:
    # If passed year is this year, return False, we want to update that report
    if date.today().year == year:
        return False
    with Session() as session:
        if (
            session.query(DividendReport)
            .filter(extract("year", DividendReport.time_from) == year)
            .one_or_none()
        ):
            return True

    return False


def end_of_or_today(input_year: int) -> str:
    today = date.today()
    if input_year < today.year:
        # Past year, so return December 31 of that year
        return date(input_year, 12, 31).isoformat()

    # Future, or ongoing year, return todays date
    return today.isoformat()
