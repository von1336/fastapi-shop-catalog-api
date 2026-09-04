import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_product(client: AsyncClient):
    cat_resp = await client.post(
        "/api/categories",
        json={"name": "Electronics", "description": "Electronic devices"},
    )
    category_id = cat_resp.json()["id"]
    response = await client.post(
        "/api/products",
        json={
            "name": "Laptop",
            "description": "Gaming laptop",
            "price": 999.99,
            "quantity": 10,
            "category_id": category_id,
            "is_active": True,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Laptop"
    assert data["price"] == 999.99
    assert data["quantity"] == 10
    assert data["category"]["id"] == category_id
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_list_products(client: AsyncClient):
    cat_resp = await client.post(
        "/api/categories",
        json={"name": "Books", "description": "Books"},
    )
    category_id = cat_resp.json()["id"]
    await client.post(
        "/api/products",
        json={
            "name": "Python Book",
            "description": "Learn Python",
            "price": 49.99,
            "quantity": 5,
            "category_id": category_id,
        },
    )
    response = await client.get("/api/products")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_list_products_filter_by_price(client: AsyncClient):
    cat_resp = await client.post(
        "/api/categories",
        json={"name": "FilterCat", "description": "For filtering"},
    )
    category_id = cat_resp.json()["id"]
    await client.post(
        "/api/products",
        json={
            "name": "Cheap Item",
            "price": 10.0,
            "quantity": 1,
            "category_id": category_id,
        },
    )
    await client.post(
        "/api/products",
        json={
            "name": "Expensive Item",
            "price": 1000.0,
            "quantity": 1,
            "category_id": category_id,
        },
    )
    response = await client.get("/api/products?min_price=50&max_price=2000")
    assert response.status_code == 200
    data = response.json()
    for item in data["items"]:
        assert 50 <= item["price"] <= 2000


@pytest.mark.asyncio
async def test_list_products_filter_by_category(client: AsyncClient):
    cat1 = await client.post("/api/categories", json={"name": "Cat1", "description": ""})
    cat2 = await client.post("/api/categories", json={"name": "Cat2", "description": ""})
    cid1, cid2 = cat1.json()["id"], cat2.json()["id"]
    await client.post(
        "/api/products",
        json={"name": "P1", "price": 1.0, "quantity": 1, "category_id": cid1},
    )
    await client.post(
        "/api/products",
        json={"name": "P2", "price": 2.0, "quantity": 1, "category_id": cid2},
    )
    response = await client.get(f"/api/products?category_id={cid1}")
    assert response.status_code == 200
    data = response.json()
    for item in data["items"]:
        assert item["category_id"] == cid1


@pytest.mark.asyncio
async def test_list_products_pagination(client: AsyncClient):
    response = await client.get("/api/products?page=1&per_page=3")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["per_page"] == 3
    assert len(data["items"]) <= 3


@pytest.mark.asyncio
async def test_get_product_detail(client: AsyncClient):
    cat_resp = await client.post(
        "/api/categories",
        json={"name": "DetailCat", "description": ""},
    )
    category_id = cat_resp.json()["id"]
    prod_resp = await client.post(
        "/api/products",
        json={
            "name": "Detail Product",
            "description": "For detail test",
            "price": 25.5,
            "quantity": 7,
            "category_id": category_id,
        },
    )
    product_id = prod_resp.json()["id"]
    response = await client.get(f"/api/products/{product_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == product_id
    assert data["name"] == "Detail Product"
    assert data["price"] == 25.5
    assert "category" in data


@pytest.mark.asyncio
async def test_get_product_not_found(client: AsyncClient):
    response = await client.get("/api/products/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_product(client: AsyncClient):
    cat_resp = await client.post(
        "/api/categories",
        json={"name": "UpdateCat", "description": ""},
    )
    category_id = cat_resp.json()["id"]
    prod_resp = await client.post(
        "/api/products",
        json={
            "name": "Original",
            "price": 10.0,
            "quantity": 1,
            "category_id": category_id,
        },
    )
    product_id = prod_resp.json()["id"]
    response = await client.put(
        f"/api/products/{product_id}",
        json={"name": "Updated", "price": 20.0},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated"
    assert data["price"] == 20.0


@pytest.mark.asyncio
async def test_delete_product(client: AsyncClient):
    cat_resp = await client.post(
        "/api/categories",
        json={"name": "DelCat", "description": ""},
    )
    category_id = cat_resp.json()["id"]
    prod_resp = await client.post(
        "/api/products",
        json={
            "name": "ToDelete",
            "price": 1.0,
            "quantity": 1,
            "category_id": category_id,
        },
    )
    product_id = prod_resp.json()["id"]
    response = await client.delete(f"/api/products/{product_id}")
    assert response.status_code == 204
    get_resp = await client.get(f"/api/products/{product_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_create_product_invalid_category(client: AsyncClient):
    response = await client.post(
        "/api/products",
        json={
            "name": "Orphan",
            "price": 1.0,
            "quantity": 1,
            "category_id": 99999,
        },
    )
    assert response.status_code == 400
