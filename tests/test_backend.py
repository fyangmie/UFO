"""Backend unit tests for the UFO FastAPI app.

Live HTTP integration is covered by scripts/smoke_test.py after Uvicorn starts.
"""

from pathlib import Path
import sys

import pytest
from pydantic import ValidationError

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.main import health, model_info, predict
from backend.schemas import PredictionRequest


def test_health_endpoint_returns_model_status() -> None:
    response = health()
    payload = response.model_dump()

    assert "status" in payload
    assert "model_loaded" in payload


def test_model_info_exposes_expected_features() -> None:
    response = model_info()
    payload = response.model_dump()

    assert payload["features"] == ["Seconds", "Latitude", "Longitude"]
    assert payload["model_path"] == "models/ufo-model.pkl"


def test_prediction_request_rejects_out_of_range_seconds() -> None:
    with pytest.raises(ValidationError):
        PredictionRequest(seconds=0, latitude=34.05, longitude=-118.25)


def test_predict_preserves_decimal_coordinates() -> None:
    health_payload = health().model_dump()
    if not health_payload.get("model_loaded"):
        pytest.skip("Model artifact is not available. Run `python scripts/train_model.py`.")

    response = predict(
        PredictionRequest(seconds=30.5, latitude=34.0522, longitude=-118.2437)
    )
    payload = response.model_dump()

    assert payload["predicted_country"]
    assert isinstance(payload["predicted_class_id"], int)
    assert "probabilities" in payload
