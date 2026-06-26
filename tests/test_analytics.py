import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_analytics_nonexistent():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/analytics/nonexistent-xyz")
        assert resp.status_code == 404


@pytest.mark.anyio
async def test_analytics_existing():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        create_resp = await client.post("/shorten", json={"url": "https://www.analytics-test.com"})
        short_code = create_resp.json()["short_code"]

        resp = await client.get(f"/analytics/{short_code}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["short_code"] == short_code
        assert "total_clicks" in data
        assert "country_breakdown" in data
