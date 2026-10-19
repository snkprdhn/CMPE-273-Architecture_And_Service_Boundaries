import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import urlopen

from flask import Flask, jsonify, request

app = Flask(__name__)

INVENTORY_URL = os.getenv("INVENTORY_URL", "http://127.0.0.1:8001")
orders = []


def item_is_available(item, quantity):
    path = f"/inventory/{quote(item)}?{urlencode({'quantity': quantity})}"
    with urlopen(f"{INVENTORY_URL}{path}", timeout=2) as response:
        return json.load(response)["available"]


@app.get("/health")
def health():
    return jsonify(status="ok")


@app.post("/orders")
def create_order():
    data = request.get_json(silent=True) or {}
    item = data.get("item")
    quantity = data.get("quantity", 1)

    if not isinstance(item, str) or not item.strip():
        return jsonify(error="item is required"), 400
    if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity < 1:
        return jsonify(error="quantity must be a positive integer"), 400

    try:
        available = item_is_available(item.strip().lower(), quantity)
    except (HTTPError, URLError, TimeoutError, OSError, KeyError, json.JSONDecodeError):
        return jsonify(error="inventory service is unavailable"), 503

    if not available:
        return jsonify(error="item is unavailable"), 409

    order = {
        "id": len(orders) + 1,
        "item": item.strip().lower(),
        "quantity": quantity,
        "status": "created",
    }
    orders.append(order)
    return jsonify(order=order), 201


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000)
