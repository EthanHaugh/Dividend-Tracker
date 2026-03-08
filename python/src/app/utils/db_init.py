from datetime import datetime

from models.models import Company
from app.db import db


def ensure_placeholder_company():
    """
    Ensure the UNKNOWN company exists for closed positions

    This is needed for Dividends which we can't retrieve an open/closed position for
    """

    placeholder = db.session.query(Company).filter(Company.ticker == "UNKNOWN").first()

    if not placeholder:
        placeholder = Company(
            ticker="UNKNOWN",
            name="Closed/Unknown Position",
            quantity=0.0,
            initial_buy_date=datetime(2000, 1, 1).date(),
            average_buy_price=0.0,
            total_payments=0.0,
        )
        db.session.add(placeholder)
        db.session.commit()
