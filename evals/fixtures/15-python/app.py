from flask import Flask, request, jsonify
from pagination import paginate

app = Flask(__name__)

ITEMS = [{"id": i, "name": f"Item {i}"} for i in range(1, 51)]


@app.route("/api/items")
def list_items():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    result = paginate(ITEMS, page, per_page)
    return jsonify(result)


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True)
