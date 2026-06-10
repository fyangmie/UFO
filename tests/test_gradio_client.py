"""Tests for the Gradio-to-FastAPI HTTP client."""

import requests

import model_service


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code
        self.ok = 200 <= status_code < 400
        self.text = ""

    def json(self):
        return self._payload


def test_backend_health_requires_loaded_model(monkeypatch) -> None:
    monkeypatch.setattr(
        model_service.requests,
        "get",
        lambda *args, **kwargs: FakeResponse(
            {"status": "ok", "model_loaded": True, "error": None}
        ),
    )

    assert model_service.backend_health()["model_loaded"] is True


def test_predict_country_calls_fastapi_with_decimal_coordinates(monkeypatch) -> None:
    captured = {}

    def fake_post(url, json, timeout):
        captured["url"] = url
        captured["json"] = json
        return FakeResponse(
            {
                "predicted_class_id": 4,
                "predicted_country": "US",
                "probabilities": {"Canada": 0.3, "US": 0.7},
            }
        )

    monkeypatch.setattr(model_service.requests, "post", fake_post)

    country, confidence, probabilities = model_service.predict_country(
        30.5,
        34.0522,
        -118.2437,
    )

    assert captured["url"].endswith("/predict")
    assert captured["json"]["latitude"] == 34.0522
    assert captured["json"]["longitude"] == -118.2437
    assert country == "US"
    assert confidence == 0.7
    assert list(probabilities) == ["US", "Canada"]


def test_predict_country_reports_backend_unavailable(monkeypatch) -> None:
    def connection_error(*args, **kwargs):
        raise requests.ConnectionError("connection refused")

    monkeypatch.setattr(model_service.requests, "post", connection_error)

    try:
        model_service.predict_country(30, 34.05, -118.25)
    except model_service.BackendClientError as exc:
        assert "unavailable" in str(exc)
    else:
        raise AssertionError("Expected BackendClientError")
