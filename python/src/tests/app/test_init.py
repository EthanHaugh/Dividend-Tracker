from unittest.mock import patch

import app as app_module
import pytest
from app import create_app, validate_config
from flask import Config, Flask


def make_config(database_uri: str, demo_mode: bool, broker_url: str = "") -> Config:
    config = Flask(__name__).config
    config.update(
        {
            "SQLALCHEMY_DATABASE_URI": database_uri,
            "DEMO_MODE": demo_mode,
            "CELERY_BROKER_URL": broker_url,
        }
    )
    return config


@pytest.mark.parametrize(
    ("database_uri", "demo_mode", "broker_url", "error"),
    [
        ("", True, "", "SQLALCHEMY_DATABASE_URI is not set"),
        ("mysql://localhost/db", True, "", "Unsupported database scheme: mysql"),
        ("sqlite://[::1", True, "", "Invalid DATABASE_URL"),
        ("sqlite:///:memory:", False, "", "CELERY_BROKER_URL is not set"),
        (
            "sqlite:///:memory:",
            False,
            "amqp://localhost",
            "Unsupported broker scheme: amqp",
        ),
        (
            "sqlite:///:memory:",
            False,
            "redis://[::1",
            "Invalid CELERY_BROKER_URL",
        ),
    ],
)
def test_validate_config_rejects_invalid_values(
    database_uri: str, demo_mode: bool, broker_url: str, error: str
) -> None:
    with pytest.raises(ValueError, match=error):
        validate_config(make_config(database_uri, demo_mode, broker_url))


def test_validate_config_skips_broker_validation_in_demo_mode() -> None:
    assert validate_config(make_config("sqlite:///:memory:", True, "amqp://localhost"))


def test_create_app_uses_flask_env_when_env_is_not_provided(monkeypatch) -> None:
    monkeypatch.setenv("FLASK_ENV", "TESTING")

    app = create_app()

    assert app.testing


def test_create_app_normalises_comma_separated_cors_origins(monkeypatch) -> None:
    class TestConstructor(app_module.config["TESTING"]):  # type: ignore
        def __init__(self) -> None:
            super().__init__()
            self.ALLOWED_ORIGINS = "https://first.example, https://second.example"

    monkeypatch.setitem(app_module.config, "TESTING", TestConstructor)
    app = create_app("TESTING")

    response = app.test_client().get(
        "/health", headers={"Origin": "https://second.example"}
    )

    assert response.headers["Access-Control-Allow-Origin"] == "https://second.example"


def test_seed_db_cli_command_seeds_placeholder_company() -> None:
    app = create_app("TESTING")

    with patch("app.ensure_placeholder_company") as ensure_placeholder_company:
        result = app.test_cli_runner().invoke(args=["seed-db"])

    assert result.exit_code == 0
    assert result.output == "Database seeded.\n"
    ensure_placeholder_company.assert_called_once_with()


def test_seed_demo_cli_command_requires_demo_mode() -> None:
    app = create_app("TESTING")

    result = app.test_cli_runner().invoke(args=["seed-demo"])

    assert isinstance(result.exception, RuntimeError)
    assert str(result.exception) == "seed-demo requires DEMO_MODE=true"


def test_seed_demo_cli_command_seeds_demo_data(monkeypatch) -> None:
    monkeypatch.setenv("DEMO_MODE", "true")
    app = create_app("TESTING")

    with patch("database.demo_seed.seed_demo_data") as seed_demo_data:
        result = app.test_cli_runner().invoke(args=["seed-demo"])

    assert result.exit_code == 0
    assert result.output == "Demo data seeded.\n"
    seed_demo_data.assert_called_once_with()


def test_demo_frontend_serves_assets_and_spa_fallback(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("DEMO_MODE", "true")
    app = create_app("TESTING")
    (tmp_path / "index.html").write_text("demo dashboard")
    (tmp_path / "asset.txt").write_text("static asset")
    app.config["DEMO_FRONTEND_DIR"] = str(tmp_path)

    client = app.test_client()

    assert client.get("/asset.txt").data == b"static asset"
    assert client.get("/nested/route").data == b"demo dashboard"


@pytest.mark.parametrize("frontend_dir_is_none", [True, False])
def test_demo_frontend_returns_404_when_unavailable(
    monkeypatch, tmp_path, frontend_dir_is_none: bool
) -> None:
    monkeypatch.setenv("DEMO_MODE", "true")
    app = create_app("TESTING")
    app.config["DEMO_FRONTEND_DIR"] = None if frontend_dir_is_none else str(tmp_path)

    response = app.test_client().get("/")

    assert response.status_code == 404
    assert response.get_json() == {"error": "Demo frontend is not available"}
