from pathlib import Path
from shutil import rmtree
from typing import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient
from main import app
from settings import config


@pytest.fixture(scope="package")
def anyio_backend():
    return "asyncio"


@pytest.fixture(name="client")
async def client_fixture() -> AsyncIterator[AsyncClient]:
    """
    TestClient for FastAPI
    """
    # pylint: disable=C0301

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"  # type: ignore
    ) as ac:
        yield ac


@pytest.fixture
def path_image() -> Path:
    return config.ROOT_DIR / "tests" / "test-image.jpg"


@pytest.fixture(scope="package", autouse=True)
async def media_dir():
    config.MEDIA_DIR.mkdir(exist_ok=True)
    yield
    rmtree(config.MEDIA_DIR)
