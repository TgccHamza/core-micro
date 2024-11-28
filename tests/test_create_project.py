def test_like_comment(client):
    response = client.post("/items/", json={"name": "Test Item", "description": "Test Description"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Item"
    assert data["description"] == "Test Description"

def test_read_item(client):
    # Create an item
    response = client.post("/items/", json={"name": "Test Item", "description": "Test Description"})
    item_id = response.json()["id"]

    # Read the item
    response = client.get(f"/items/{item_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Item"
    assert data["description"] == "Test Description"
