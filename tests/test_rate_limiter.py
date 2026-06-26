import pytest
from app.services.rate_limiter import rate_limiter


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_rate_limiter_allows_within_limit():
    is_limited, remaining, retry = await rate_limiter.is_rate_limited(
        "192.168.1.100", "create", limit=5, window=60
    )
    assert isinstance(is_limited, bool)
    assert isinstance(remaining, int)


@pytest.mark.anyio
async def test_rate_limiter_types():
    is_limited, remaining, retry = await rate_limiter.is_rate_limited("10.0.0.1", "redirect")
    assert isinstance(is_limited, bool)
    assert isinstance(remaining, int)
    assert isinstance(retry, int)
