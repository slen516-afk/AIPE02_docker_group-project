from __future__ import annotations

import os

import requests
from flask import Flask, Response, jsonify, render_template

app = Flask(__name__)

BACKEND_URL = os.environ["BACKEND_API_URL"].rstrip("/")


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/health")
def health():
    return jsonify({"ok": True})


@app.get("/api/data")
def api_data():
    # 前端代理到後端 API
    try:
        r = requests.get(f"{BACKEND_URL}/api/data", timeout=20)
        return Response(
            r.content,
            status=r.status_code,
            content_type=r.headers.get("Content-Type", "application/json"),
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 502


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
