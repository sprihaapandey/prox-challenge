import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "backend"))

import pytest
from dotenv import load_dotenv

load_dotenv(REPO_ROOT / ".env")

from db.session import new_session  # noqa: E402


@pytest.fixture()
def db():
    session = new_session()
    try:
        yield session
    finally:
        session.close()
