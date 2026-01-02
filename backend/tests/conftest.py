import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("JWT_SECRET", "test-secret")
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_hids.db")
os.environ.setdefault("LOG_LEVEL", "INFO")

db_path = Path("test_hids.db")
if db_path.exists():
    db_path.unlink()

from app.main import app  # noqa: E402
from app.core.security import get_current_active_user  # noqa: E402


class DummyUser:
    is_admin = True
    is_active = True
    id = 1


def _override_current_user():
    return DummyUser()


app.dependency_overrides[get_current_active_user] = _override_current_user


@pytest.fixture()
def client():
    return TestClient(app)
