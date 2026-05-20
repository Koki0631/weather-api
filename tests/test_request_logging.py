import logging

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

from app.logging_config import configure_logging
from app.main import app
from app.middleware.request_logging import RequestLoggingMiddleware

configure_logging()


@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as http_client:
        yield http_client


@pytest.mark.asyncio
async def test_request_logging_logs_success(client, caplog: pytest.LogCaptureFixture):
    caplog.set_level(logging.INFO, logger="app.middleware.request_logging")

    response = await client.get("/docs")

    assert response.status_code == 200
    assert "GET /docs -> 200" in caplog.text
    assert "ms)" in caplog.text


def test_request_logging_logs_exception(caplog: pytest.LogCaptureFixture):
    caplog.set_level(logging.ERROR, logger="app.middleware.request_logging")

    test_app = FastAPI()
    test_app.add_middleware(RequestLoggingMiddleware)

    @test_app.get("/boom")
    def boom() -> None:
        raise RuntimeError("test failure")

    client = TestClient(test_app, raise_server_exceptions=False)
    response = client.get("/boom")

    assert response.status_code == 500
    assert "GET /boom -> error" in caplog.text
    assert "test failure" in caplog.text
