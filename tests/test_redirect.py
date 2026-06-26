import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_redirect_existing_url():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", follow_redirects=False) as client:
        create_resp = await client.post("/shorten", json={"url": "https://www.python.org"})
        short_code = create_resp.json()["short_code"]

        resp = await client.get(f"/{short_code}")
        assert resp.status_code in (301, 302)
        assert resp.headers.get("location") == "https://www.python.org"


@pytest.mark.anyio
async def test_redirect_nonexistent():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/nonexistent-code-xyz")
        assert resp.status_code == 404


@pytest.mark.anyio
async def test_delete_url():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", follow_redirects=False) as client:
        create_resp = await client.post("/shorten", json={"url": "https://www.delete-me.com"})
        short_code = create_resp.json()["short_code"]

        del_resp = await client.delete(f"/{short_code}")
        assert del_resp.status_code == 200

        redirect_resp = await client.get(f"/{short_code}")
        assert redirect_resp.status_code == 410
