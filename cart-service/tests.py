# Test the cart service API

import os
import pytest
import redis
from fastapi.testclient import TestClient
from app import app, Item

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_redis():
    with redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        db=0,
    ) as database:
        database.flushdb()


def test_get_user_items():
    user_id = 1
    response = client.get(f"/cart/{user_id}")
    assert response.status_code == 200
    assert "user_id" in response.json()
    assert "items" in response.json()

def test_add_user_item():
    user_id = 1
    item = Item(id=1, name="Test Item", priceCents=100)
    response = client.post(f"/cart/{user_id}", json=item.model_dump())
    assert response.status_code == 201
    assert response.json() == {"message": f"Item {item.id} added to user {user_id}'s cart."}

def test_delete_user_item():
    user_id = 1
    item_id = 1
    response = client.post(f"/cart/{user_id}", json={"id": item_id, "name": "Test Item", "priceCents": 100})
    assert response.status_code == 201

    response = client.delete(f"/cart/{user_id}", params={"item_id": item_id})
    assert response.status_code == 204

def test_delete_nonexistent_item():
    user_id = 1
    item_id = 999  
    response = client.delete(f"/cart/{user_id}", params={"item_id": item_id})
    assert response.status_code == 204

def test_add_and_get_user_items():
    user_id = 2
    item1 = Item(id=1, name="Item 1", priceCents=100)
    item2 = Item(id=2, name="Item 2", priceCents=200)

    client.post(f"/cart/{user_id}", json=item1.model_dump())
    client.post(f"/cart/{user_id}", json=item2.model_dump())

    response = client.get(f"/cart/{user_id}")
    assert response.status_code == 200
    items = response.json()["items"]
    assert isinstance(items, list)
    assert len(items) == 2
    assert any(item["id"] == item1.id for item in items)
    assert any(item["id"] == item2.id for item in items)