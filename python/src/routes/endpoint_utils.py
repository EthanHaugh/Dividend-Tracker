from datetime import date


def end_of_or_today(input_year: int) -> str:
    today = date.today()
    if input_year < today.year:
        # Past year, so return December 31 of that year
        return date(input_year, 12, 31).isoformat()

    # Future, or ongoing year, return todays date
    return today.isoformat()
