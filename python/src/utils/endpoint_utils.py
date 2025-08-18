from db import Session
from sqlalchemy import extract
from models.models import DividendReport


def assert_report_with_date_does_not_exist(year: int) -> bool:
    with Session() as session:
        if (
            session.query(DividendReport)
            .filter(extract("year", DividendReport.time_from) == year)
            .one_or_none()
        ):
            return True

    return False
