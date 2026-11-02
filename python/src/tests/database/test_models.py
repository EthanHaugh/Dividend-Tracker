from decimal import Decimal

from database.models import Dividend


class TestDatabaseModels:
    def test_dividend_model_as_dict(self) -> None:
        dividend = Dividend(
            dividend_id=1,
            report_id=1,
            company_id=1,
            payment_date="2024-03-01",
            year=2024,
            total_payment=Decimal("15.00"),
            number_of_shares=10.0,
            currency="USD",
            created_at="2024-01-01T00=00=00",
        )

        assert dividend.asdict() == {
            "dividend_id": 1,
            "report_id": 1,
            "company_id": 1,
            "company_name": None,
            "ticker": None,
            "payment_date": "2024-03-01",
            "year": 2024,
            "total_payment": Decimal("15.00"),
            "number_of_shares": 10.0,
            "currency": "USD",
            "created_at": "2024-01-01T00=00=00",
        }
