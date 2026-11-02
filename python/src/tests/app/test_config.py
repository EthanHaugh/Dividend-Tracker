from app.config import Config, config
from sqlalchemy import NullPool


def test_config_dictionary() -> None:
    assert config["DEVELOPMENT"]
    assert config["TESTING"]


def test_base_config() -> None:
    test_config = Config()

    assert test_config.ALLOWED_ORIGINS == ["http://localhost:3000"]
    assert test_config.SQLALCHEMY_TRACK_MODIFICATIONS == False
    assert test_config.DEMO_MODE == False


def test_development_config() -> None:
    dev_config = config["DEVELOPMENT"]()

    assert dev_config.DEBUG == True
    assert dev_config.BASE_DIR.endswith("/python/src")
    assert dev_config.INSTANCE_DIR.endswith("/python/src/instance")
    assert dev_config.SQLALCHEMY_DATABASE_URI.endswith(
        "/python/src/instance/dividends.db"
    )
    assert dev_config.SQLALCHEMY_ENGINE_OPTIONS == {"poolclass": NullPool}


def test_testing_config() -> None:
    test_config = config["TESTING"]()

    assert test_config.TESTING == True
    assert test_config.SQLALCHEMY_DATABASE_URI == "sqlite:///:memory:"
    assert test_config.SQLALCHEMY_ENGINE_OPTIONS == {"poolclass": NullPool}
