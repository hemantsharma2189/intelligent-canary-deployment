import os
import random
import time

from flask import Flask, jsonify
from prometheus_client import (
    Counter,
    Histogram,
    generate_latest,
    CONTENT_TYPE_LATEST,
)

app = Flask(__name__)

APP_VERSION = os.getenv(
    "APP_VERSION",
    "v1-stable",
)

FAILURE_RATE = float(
    os.getenv("FAILURE_RATE", "0")
)

REQUESTS = Counter(
    "canary_http_requests_total",
    "Total HTTP requests",
    ["version", "status"],
)

LATENCY = Histogram(
    "canary_http_request_duration_seconds",
    "HTTP request latency",
    ["version"],
)


@app.route("/")
def home():
    start_time = time.time()

    if random.random() < FAILURE_RATE:
        REQUESTS.labels(
            version=APP_VERSION,
            status="500",
        ).inc()

        LATENCY.labels(
            version=APP_VERSION,
        ).observe(time.time() - start_time)

        return jsonify(
            {
                "status": "error",
                "version": APP_VERSION,
                "message": "Simulated canary failure",
            }
        ), 500

    REQUESTS.labels(
        version=APP_VERSION,
        status="200",
    ).inc()

    LATENCY.labels(
        version=APP_VERSION,
    ).observe(time.time() - start_time)

    return jsonify(
        {
            "status": "success",
            "version": APP_VERSION,
            "message": "Canary demo application",
        }
    )


@app.route("/health")
def health():
    return jsonify(
        {
            "status": "healthy",
            "version": APP_VERSION,
        }
    )


@app.route("/ready")
def ready():
    return jsonify(
        {
            "status": "ready",
            "version": APP_VERSION,
        }
    )


@app.route("/metrics")
def metrics():
    return (
        generate_latest(),
        200,
        {
            "Content-Type": CONTENT_TYPE_LATEST,
        },
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8080,
    )
