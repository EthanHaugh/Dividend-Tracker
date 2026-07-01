from datetime import datetime, date

from utils.endpoint_utils import end_of_or_today


class TestEndOfOrToday:
    def test_input_year_less_than_current_year(self):
        result = end_of_or_today(2020)

        assert result == "2020-12-31"

    def test_input_year_current_year(self):
        result = end_of_or_today(datetime.now().year)

        assert result == str(date.today())

    def test_input_year_greater_than_current_year(self):
        # No matter how far in advance the function,
        # we should always get the todays date.
        result = end_of_or_today(datetime.now().year + 10)

        assert result == str(date.today())
