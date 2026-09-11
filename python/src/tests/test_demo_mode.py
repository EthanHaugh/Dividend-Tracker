import pytest
from app import create_app
from database.db import db
from database.demo_seed import seed_demo_data


@pytest.fixture
def demo_app(monkeypatch):
    monkeypatch.setenv("DEMO_MODE", "true")
    app = create_app("TESTING")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


def test_demo_mode_excludes_update_route_and_seeds_dashboard_data(demo_app, tmp_path):
    with demo_app.app_context():
        seed_demo_data()
        seed_demo_data()
        demo_app.config["DEMO_FRONTEND_DIR"] = str(tmp_path)
        demo_app.static_folder = str(tmp_path / "static")
        (tmp_path / "index.html").write_text("demo dashboard")

    client = demo_app.test_client()
    assert client.get("/").status_code == 200
    assert client.get("/health").status_code == 200
    assert client.get("/download?year=2026").status_code == 404
    assert len(client.get("/open-positions").get_json()) == 3
    assert len(client.get("/yearly-dividends").get_json()) == 4
    assert client.get("/total-dividends").get_json()["total_dividends"] > 0
    assert client.get("/pie-chart").get_json()["total_count"] == 3
    assert client.get("/list-company-totals").get_json()["total_count"] == 3
    assert len(client.get("/monthly-dividends-comparison").get_json()["data"]) == 12
