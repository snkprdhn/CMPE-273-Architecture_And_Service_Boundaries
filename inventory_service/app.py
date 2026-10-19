from flask import Flask, jsonify, request

app = Flask(__name__)

INVENTORY = {
    "keyboard": 5,
    "monitor": 2,
    "webcam": 0,
}


@app.get("/health")
def health():
    return jsonify(status="ok")


@app.get("/inventory/<item>")
def check_inventory(item):
    try:
        quantity = int(request.args.get("quantity", 1))
    except ValueError:
        return jsonify(error="quantity must be a positive integer"), 400

    if quantity < 1:
        return jsonify(error="quantity must be a positive integer"), 400

    stock = INVENTORY.get(item.lower(), 0)
    return jsonify(
        item=item.lower(),
        quantity=quantity,
        stock=stock,
        available=stock >= quantity,
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8001)
