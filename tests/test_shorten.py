import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_shorten_valid_url():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/shorten", json={"url": "https://www.google.com"})
        assert response.status_code == 200
        data = response.json()
        assert "short_code" in data
        assert "short_url" in data
        assert data["long_url"] == "https://www.google.com"


@pytest.mark.anyio
async def test_shorten_invalid_url():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/shorten", json={"url": "not-a-url"})
        assert response.status_code == 422


@pytest.mark.anyio
async def test_shorten_custom_alias():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/shorten", json={
            "url": "https://www.example.com",
            "custom_alias": "my-link"
        })
        assert response.status_code == 200
        assert response.json()["short_code"] == "my-link"


@pytest.mark.anyio
async def test_shorten_with_expiry():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/shorten", json={
            "url": "https://www.example.com",
            "expiry_date": "2099-12-31T23:59:59"
        })
        assert response.status_code == 200
        assert response.json()["expiry_date"] is not None
