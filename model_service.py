"""Small Gradio-facing wrapper around the saved UFO model artifact."""

from typing import Dict, Tuple

from backend.model_service import get_model_service


def predict_country(seconds: float, latitude: float, longitude: float) -> Tuple[str, float, Dict[str, float]]:
    """Return country, confidence, and probabilities for the Gradio Space."""

    service = get_model_service()
    service.load()

    if not service.is_loaded:
        raise RuntimeError(service.load_error or "Model artifact is not loaded.")

    result = service.predict(
        seconds=float(seconds),
        latitude=float(latitude),
        longitude=float(longitude),
    )
    country = result["predicted_country"]
    probabilities = result.get("probabilities") or {}
    confidence = float(probabilities.get(country, 0.0))

    ranked = dict(
        sorted(
            probabilities.items(),
            key=lambda item: item[1],
            reverse=True,
        )
    )
    return country, confidence, ranked
