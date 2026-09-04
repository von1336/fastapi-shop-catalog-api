import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_category(client: AsyncClient):
    response = await client.post(
        "/api/categories",
        json={"name": "Electronics", "description": "Electronic devices"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Electronics"
    assert data["description"] == "Electronic devices"
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_list_categories(client: AsyncClient):
    await client.post("/api/categories", json={"name": "Books", "description": "Books category"})
    response = await client.get("/api/categories")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 1
    assert len(data["items"]) >= 1


@pytest.mark.asyncio
async def test_list_categories_pagination(client: AsyncClient):
    response = await client.get("/api/categories?page=1&per_page=5")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "page" in data
    assert "per_page" in data
    assert data["page"] == 1
    assert data["per_page"] == 5


@pytest.mark.asyncio
async def test_get_category_detail(client: AsyncClient):
    create_resp = await client.post(
        "/api/categories",
        json={"name": "Clothing", "description": "Clothing items"},
    )
    category_id = create_resp.json()["id"]
    response = await client.get(f"/api/categories/{category_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == category_id
    assert data["name"] == "Clothing"
    assert data["description"] == "Clothing items"


@pytest.mark.asyncio
async def test_get_category_not_found(client: AsyncClient):
    response = await client.get("/api/categories/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_category(client: AsyncClient):
    create_resp = await client.post(
        "/api/categories",
        json={"name": "Toys", "description": "Original"},
    )
    category_id = create_resp.json()["id"]
    response = await client.put(
        f"/api/categories/{category_id}",
        json={"name": "Toys Updated", "description": "Updated description"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Toys Updated"
    assert data["description"] == "Updated description"


@pytest.mark.asyncio
async def test_update_category_partial(client: AsyncClient):
    create_resp = await client.post(
        "/api/categories",
        json={"name": "Sports", "description": "Sports items"},
    )
    category_id = create_resp.json()["id"]
    response = await client.put(
        f"/api/categories/{category_id}",
        json={"description": "Only description updated"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Sports"
    assert data["description"] == "Only description updated"


@pytest.mark.asyncio
async def test_delete_category(client: AsyncClient):
    create_resp = await client.post(
        "/api/categories",
        json={"name": "ToDelete", "description": "Will be deleted"},
    )
    category_id = create_resp.json()["id"]
    response = await client.delete(f"/api/categories/{category_id}")
    assert response.status_code == 204
    get_resp = await client.get(f"/api/categories/{category_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_category_not_found(client: AsyncClient):
    response = await client.delete("/api/categories/99999")
    assert response.status_code == 404
