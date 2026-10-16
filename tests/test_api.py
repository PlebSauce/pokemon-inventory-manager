import pytest
from fastapi.testclient import TestClient

from pokemon_inventory.api import create_app


@pytest.fixture
def client():
    app = create_app("sqlite:///:memory:")
    with TestClient(app) as test_client:
        yield test_client


def test_create_list_and_get_card(client):
    response = client.post(
        "/cards",
        json={"name": "Pikachu", "set_name": "Base", "number": "1", "quantity": 3},
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload["name"] == "Pikachu"
    assert payload["quantity"] == 3
    card_id = payload["id"]

    list_response = client.get("/cards")
    assert list_response.status_code == 200
    cards = list_response.json()
    assert any(card["id"] == card_id for card in cards)

    get_response = client.get(f"/cards/{card_id}")
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Pikachu"


def test_duplicate_card_is_rejected(client):
    client.post(
        "/cards",
        json={"name": "Bulbasaur", "set_name": "Base", "number": "2", "quantity": 2},
    )

    response = client.post(
        "/cards",
        json={"name": "Bulbasaur", "set_name": "Base", "number": "2", "quantity": 4},
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()


def test_missing_card_returns_404(client):
    response = client.get("/cards/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Card not found"


def test_invalid_input_is_rejected(client):
    response = client.post(
        "/cards",
        json={"name": "   ", "set_name": "Base", "number": "1", "quantity": 0},
    )
    assert response.status_code == 422


def test_update_and_delete_card(client):
    create_response = client.post(
        "/cards",
        json={"name": "Charmander", "set_name": "Base", "number": "3", "quantity": 1},
    )
    card_id = create_response.json()["id"]

    update_response = client.put(
        f"/cards/{card_id}",
        json={"quantity": 5, "set_name": "Jungle"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["quantity"] == 5
    assert update_response.json()["set_name"] == "Jungle"

    delete_response = client.delete(f"/cards/{card_id}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/cards/{card_id}")
    assert get_response.status_code == 404


def test_inventory_summary(client):
    client.post(
        "/cards",
        json={"name": "Squirtle", "set_name": "Base", "number": "4", "quantity": 2},
    )
    client.post(
        "/cards",
        json={"name": "Gengar", "set_name": "Jungle", "number": "7", "quantity": 1},
    )

    response = client.get("/inventory/summary")
    assert response.status_code == 200
    summary = response.json()
    assert summary["total_cards"] >= 3
    assert summary["unique_cards"] >= 2
