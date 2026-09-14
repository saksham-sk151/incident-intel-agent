import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Use an isolated, throwaway SQLite DB for tests so we never touch the dev DB.
os.environ["DATABASE_URL"] = f"sqlite:///{Path(__file__).resolve().parent / 'test.db'}"

from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c
