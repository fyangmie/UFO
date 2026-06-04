"""Shared backend configuration for local paths and model metadata."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = PROJECT_ROOT / "models" / "ufo-model.pkl"
LABEL_MAPPING_PATH = PROJECT_ROOT / "models" / "label_mapping.json"

FEATURE_NAMES = ["Seconds", "Latitude", "Longitude"]
APP_NAME = "UFO Country Predictor API"
