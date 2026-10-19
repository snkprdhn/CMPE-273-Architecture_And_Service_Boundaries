import json
import sys
import unittest
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from inventory_service.app import app as inventory_app
from order_service.app import app as order_app, orders


class FakeResponse(BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.client = inventory_app.test_client()

    def test_reports_available_stock(self):
        response = self.client.get("/inventory/keyboard?quantity=2")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()["available"])

    def test_reports_unavailable_stock(self):
        response = self.client.get("/inventory/webcam?quantity=1")
        self.assertFalse(response.get_json()["available"])


class OrderTests(unittest.TestCase):
    def setUp(self):
        orders.clear()
        self.client = order_app.test_client()

    @patch("order_service.app.urlopen")
    def test_creates_order_when_item_is_available(self, mock_urlopen):
        mock_urlopen.return_value = FakeResponse(json.dumps({"available": True}).encode())
        response = self.client.post("/orders", json={"item": "keyboard", "quantity": 2})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["order"]["status"], "created")

    @patch("order_service.app.urlopen", side_effect=OSError)
    def test_stays_running_when_inventory_is_down(self, _mock_urlopen):
        response = self.client.post("/orders", json={"item": "keyboard"})
        self.assertEqual(response.status_code, 503)
        self.assertEqual(self.client.get("/health").status_code, 200)

    def test_rejects_invalid_quantity(self):
        response = self.client.post("/orders", json={"item": "keyboard", "quantity": 0})
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
