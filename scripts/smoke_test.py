"""Smoke test for the local FastAPI UFO backend."""

import json
import os
import sys
from typing import Any, Dict

import requests


BASE_URL = os.getenv("UFO_API_BASE_URL", "http://127.0.0.1:8000")
TIMEOUT_SECONDS = 5
SAMPLE_REQUEST = {
    "seconds": 30,
    "latitude": 34.05,
    "longitude": -118.25,
}


def print_json(title: str, payload: Dict[str, Any]) -> None:
    print(title)
    print(json.dumps(payload, indent=2))


def main() -> int:
    try:
        health_response = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT_SECONDS)
        health_response.raise_for_status()
        health = health_response.json()
        print_json("GET /health", health)
    except requests.RequestException as exc:
        print(f"Health check failed: {exc}")
        return 1

    if not health.get("model_loaded"):
        print("Backend is running, but the model is not loaded.")
        return 1

    try:
        prediction_response = requests.post(
            f"{BASE_URL}/predict",
            json=SAMPLE_REQUEST,
            timeout=TIMEOUT_SECONDS,
        )
        prediction_response.raise_for_status()
        print_json("POST /predict", prediction_response.json())
    except requests.RequestException as exc:
        print(f"Prediction failed: {exc}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
