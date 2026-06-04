"""Pydantic schemas for the UFO prediction API."""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    """Validated request body for a single UFO country prediction."""

    seconds: float = Field(
        ...,
        ge=1,
        le=60,
        description="Duration of the UFO sighting in seconds, from 1 to 60.",
    )
    latitude: float = Field(
        ...,
        ge=-90,
        le=90,
        description="Decimal latitude of the sighting location.",
    )
    longitude: float = Field(
        ...,
        ge=-180,
        le=180,
        description="Decimal longitude of the sighting location.",
    )


class PredictionResponse(BaseModel):
    """JSON response returned by the prediction endpoint."""

    predicted_class_id: int
    predicted_country: str
    probabilities: Optional[Dict[str, float]] = None


class HealthResponse(BaseModel):
    """Health-check response for the API and model artifact."""

    status: str
    model_loaded: bool
    error: Optional[str] = None


class ModelInfoResponse(BaseModel):
    """Model metadata useful for demos and debugging."""

    model_type: Optional[str]
    features: List[str]
    classes: List[str]
    model_path: str
