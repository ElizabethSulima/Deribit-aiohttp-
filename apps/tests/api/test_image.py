from pathlib import Path

import pytest
from fastapi import status
from httpx import AsyncClient


pytestmark = pytest.mark.anyio


async def test_create_image(client: AsyncClient, path_image: Path):
    response = await client.post("/tags/", json={"name": "dom"})
    await client.post("/tags/", json={"name": "maf"})
    await client.post("/tags/", json={"name": "pop"})
    data = {"resolutions": ["100x100", "500x500"], "tags": [1, 2]}
    with open(path_image, "rb") as file:
        response = await client.post(
            "/images/", files={"image": file}, data=data
        )
    assert response.status_code == status.HTTP_201_CREATED


async def test_update_image(client: AsyncClient, path_image: Path):
    response = await client.post("/tags/", json={"name": "dom"})
    await client.post("/tags/", json={"name": "maf"})
    await client.post("/tags/", json={"name": "pop"})
    data = {"resolutions": ["100x100", "500x500"], "tags": [1, 2]}

    with open(path_image, "rb") as file:
        await client.post("/images/", files={"image": file}, data=data)
    update_data = {"tags": [1, 2, 3], "title": "skala"}
    response = await client.patch("/images/1/", json=update_data)
    assert response.status_code == status.HTTP_200_OK


async def test_delete_image(client: AsyncClient, path_image: Path):
    await client.post("/tags/", json={"name": "pop"})
    data = {"resolutions": ["100x100", "500x500"], "tags": [1]}
    with open(path_image, "rb") as file:
        await client.post("/images/", files={"image": file}, data=data)

    response = await client.delete("/images/1/")
    assert response.status_code == status.HTTP_200_OK
