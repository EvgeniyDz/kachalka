from httpx import ASGITransport, AsyncClient

from app.main import app


async def test_health_check_returns_service_status() -> None:
    """The health endpoint reports that the API is ready to accept requests."""

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "Kachalka API",
        "environment": "development",
    }