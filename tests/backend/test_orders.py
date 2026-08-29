"""
Tests for orders API endpoints, including restocking orders.
"""
import pytest
from datetime import datetime


class TestOrdersEndpoints:
    """Test suite for orders-related endpoints."""

    def test_get_all_orders(self, client):
        """Test getting all orders."""
        response = client.get("/api/orders")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

        first_order = data[0]
        assert "id" in first_order
        assert "order_number" in first_order
        assert "status" in first_order

    def test_get_order_by_id(self, client):
        """Test getting a specific order by ID."""
        all_orders = client.get("/api/orders").json()
        order_id = all_orders[0]["id"]

        response = client.get(f"/api/orders/{order_id}")
        assert response.status_code == 200
        assert response.json()["id"] == order_id

    def test_get_nonexistent_order(self, client):
        """Test getting an order that doesn't exist."""
        response = client.get("/api/orders/nonexistent-order-999")
        assert response.status_code == 404

        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_order_status_values(self, client):
        """Test that orders have valid status values."""
        data = client.get("/api/orders").json()
        valid_statuses = ["delivered", "shipped", "processing", "backordered"]

        for order in data:
            assert order["status"].lower() in valid_statuses


class TestRestockOrderEndpoint:
    """Test suite for the POST /api/orders/restock endpoint."""

    def test_create_restock_order_success(self, client):
        """Test creating a restocking order with a single item."""
        payload = {
            "budget": 10000,
            "items": [
                {"item_sku": "FLT-405", "item_name": "Oil Filter Cartridge", "quantity": 100, "unit_cost": 14.25}
            ]
        }
        response = client.post("/api/orders/restock", json=payload)
        assert response.status_code == 201

        order = response.json()
        assert order["status"] == "Processing"
        assert order["source"] == "restocking"
        assert order["items"][0]["sku"] == "FLT-405"
        assert order["items"][0]["quantity"] == 100
        assert abs(order["total_value"] - 1425.0) < 0.01
        assert order["order_number"].startswith("ORD-")

    def test_create_restock_order_multiple_items(self, client):
        """Test creating a restocking order with multiple items sums total_value correctly."""
        payload = {
            "budget": 5000,
            "items": [
                {"item_sku": "GSK-203", "item_name": "High-Temperature Gasket", "quantity": 20, "unit_cost": 9.75},
                {"item_sku": "VLV-506", "item_name": "Pressure Relief Valve", "quantity": 5, "unit_cost": 65.0}
            ]
        }
        response = client.post("/api/orders/restock", json=payload)
        assert response.status_code == 201

        order = response.json()
        assert len(order["items"]) == 2
        assert abs(order["total_value"] - (20 * 9.75 + 5 * 65.0)) < 0.01

    def test_restock_order_lead_time_is_14_days(self, client):
        """Test that the restocking order's delivery lead time is 14 days."""
        payload = {
            "budget": 500,
            "items": [{"item_sku": "GSK-203", "item_name": "High-Temperature Gasket", "quantity": 10, "unit_cost": 9.75}]
        }
        order = client.post("/api/orders/restock", json=payload).json()

        order_date = datetime.fromisoformat(order["order_date"])
        expected_delivery = datetime.fromisoformat(order["expected_delivery"])
        assert (expected_delivery - order_date).days == 14

    def test_restock_order_appears_in_get_orders(self, client):
        """Test that a placed restock order is immediately visible via GET /api/orders."""
        payload = {
            "budget": 1000,
            "items": [{"item_sku": "VLV-506", "item_name": "Pressure Relief Valve", "quantity": 5, "unit_cost": 65.0}]
        }
        created = client.post("/api/orders/restock", json=payload).json()

        all_orders = client.get("/api/orders").json()
        matching = [o for o in all_orders if o["id"] == created["id"]]
        assert len(matching) == 1
        assert matching[0]["source"] == "restocking"

    def test_create_restock_order_empty_items_fails(self, client):
        """Test that placing a restock order with no items returns 400."""
        response = client.post("/api/orders/restock", json={"budget": 100, "items": []})
        assert response.status_code == 400

    def test_create_restock_order_invalid_quantity_fails(self, client):
        """Test that a non-positive quantity returns 400."""
        payload = {
            "budget": 100,
            "items": [{"item_sku": "WDG-001", "item_name": "Industrial Widget Type A", "quantity": 0, "unit_cost": 42.0}]
        }
        response = client.post("/api/orders/restock", json=payload)
        assert response.status_code == 400
