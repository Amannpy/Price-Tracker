from fastapi.testclient import TestClient
from unittest.mock import patch

from services.api.app import app


client = TestClient(app)


@patch("services.api.routes.products.get_conn")
def test_list_products_ok(mock_conn):
    mock_cursor = mock_conn.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value
    mock_cursor.fetchall.return_value = [
        {
            "id": "prod-1",
            "sku": "PHONE-001",
            "title": "Test Phone",
            "brand": "TestBrand",
            "created_at": "2024-01-01T00:00:00Z",
        }
    ]
    resp = client.get("/products/")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["sku"] == "PHONE-001"


def test_healthz():
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


