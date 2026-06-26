import os
import pytest

os.environ["SQLITE_FALLBACK"] = "true"
os.environ["SQLITE_URL"] = "sqlite+aiosqlite:///./test_urlshortener.db"
os.environ["DEBUG"] = "false"
os.environ["BASE_URL"] = "http://test"


@pytest.fixture(autouse=True)
def cleanup_test_db():
    yield
    try:
        if os.path.exists("test_urlshortener.db"):
            os.remove("test_urlshortener.db")
    except Exception:
        pass
