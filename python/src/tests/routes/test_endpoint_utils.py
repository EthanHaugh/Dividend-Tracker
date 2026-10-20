from datetime import UTC, datetime

from utils.endpoint_utils import end_of_or_today


class TestEndOfOrToday:
    def test_input_year_less_than_current_year(self):
        result = end_of_or_today(2020)

        assert result == "2020-12-31"

    def test_input_year_current_year(self):
        result = end_of_or_today(datetime.now(tz=UTC).date().year)

        assert result == str(datetime.now(tz=UTC).date())

    def test_input_year_greater_than_current_year(self):
        # No matter how far in advance the function,
        # we should always get the todays date.
        result = end_of_or_today(datetime.now(tz=UTC).year + 10)

        assert result == str(datetime.now(tz=UTC).date())
