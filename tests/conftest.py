import pytest
from fastapi.testclient import TestClient

from app.config import Settings, get_settings
from app.db import init_db
from app.main import app


@pytest.fixture
def client(tmp_path):
    db_path = str(tmp_path / "test_usage.db")
    settings = Settings(app_name="examate-rag", environment="test", usage_db_path=db_path)
    init_db(db_path)
    app.dependency_overrides[get_settings] = lambda: settings
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
