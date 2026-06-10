"""HTTP client used by the public Gradio frontend."""

import os
from typing import Any, Dict, Tuple

import requests


DEFAULT_BACKEND_URL = "http://127.0.0.1:8000"
DEFAULT_TIMEOUT_SECONDS = 8.0


class BackendClientError(RuntimeError):
    """Raised when the Gradio frontend cannot obtain a valid API response."""


def _backend_url() -> str:
    return os.getenv("UFO_BACKEND_URL", DEFAULT_BACKEND_URL).rstrip("/")


def _timeout_seconds() -> float:
    return float(os.getenv("UFO_REQUEST_TIMEOUT", str(DEFAULT_TIMEOUT_SECONDS)))


def _error_detail(response: requests.Response) -> str:
    try:
        payload = response.json()
    except ValueError:
        return response.text or f"HTTP {response.status_code}"

    detail = payload.get("detail") if isinstance(payload, dict) else payload
    return str(detail or f"HTTP {response.status_code}")


def backend_health() -> Dict[str, Any]:
    """Return the FastAPI health response or raise a readable client error."""

    try:
        response = requests.get(
            f"{_backend_url()}/health",
            timeout=_timeout_seconds(),
        )
    except requests.ConnectionError as exc:
        raise BackendClientError("FastAPI backend is unavailable.") from exc
    except requests.Timeout as exc:
        raise BackendClientError("FastAPI backend health check timed out.") from exc
    except requests.RequestException as exc:
        raise BackendClientError(f"FastAPI health check failed: {exc}") from exc

    if not response.ok:
        raise BackendClientError(
            f"FastAPI health check returned an error: {_error_detail(response)}"
        )

    try:
        payload = response.json()
    except ValueError as exc:
        raise BackendClientError("FastAPI health response was not valid JSON.") from exc

    if not payload.get("model_loaded"):
        raise BackendClientError(
            payload.get("error") or "FastAPI is running, but the model is not loaded."
        )

    return payload


def predict_country(
    seconds: float,
    latitude: float,
    longitude: float,
) -> Tuple[str, float, Dict[str, float]]:
    """Call FastAPI and return country, confidence, and ranked probabilities."""

    request_payload = {
        "seconds": float(seconds),
        "latitude": float(latitude),
        "longitude": float(longitude),
    }

    try:
        response = requests.post(
            f"{_backend_url()}/predict",
            json=request_payload,
            timeout=_timeout_seconds(),
        )
    except requests.ConnectionError as exc:
        raise BackendClientError("FastAPI backend is unavailable.") from exc
    except requests.Timeout as exc:
        raise BackendClientError("Prediction request timed out.") from exc
    except requests.RequestException as exc:
        raise BackendClientError(f"Prediction request failed: {exc}") from exc

    if not response.ok:
        raise BackendClientError(
            f"FastAPI prediction returned an error: {_error_detail(response)}"
        )

    try:
        result = response.json()
    except ValueError as exc:
        raise BackendClientError("FastAPI prediction response was not valid JSON.") from exc

    country = result.get("predicted_country")
    if not country:
        raise BackendClientError("FastAPI response did not include a predicted country.")

    raw_probabilities = result.get("probabilities") or {}
    probabilities = {
        str(label): float(probability)
        for label, probability in raw_probabilities.items()
    }
    ranked = dict(
        sorted(
            probabilities.items(),
            key=lambda item: item[1],
            reverse=True,
        )
    )
    confidence = float(probabilities.get(country, 0.0))
    return str(country), confidence, ranked
