"""Model loading and inference helpers for the UFO FastAPI backend."""

from functools import lru_cache
import json
import pickle
from typing import Any, Dict, List, Optional

import joblib
import numpy as np
import pandas as pd

from .config import FEATURE_NAMES, LABEL_MAPPING_PATH, MODEL_PATH


class ModelService:
    """Load the saved scikit-learn model once and reuse it for predictions."""

    def __init__(self) -> None:
        self.model: Optional[Any] = None
        self.class_id_to_country: Dict[str, str] = {}
        self.class_labels: List[str] = []
        self.load_error: Optional[str] = None
        self._load_attempted = False

    @property
    def is_loaded(self) -> bool:
        return self.model is not None and self.load_error is None

    def load(self, force: bool = False) -> None:
        """Load the model and label mapping once per process."""

        if self._load_attempted and not force:
            return

        self._load_attempted = True
        self.load_error = None

        if not MODEL_PATH.exists():
            self.model = None
            self.load_error = (
                f"Model artifact not found at {MODEL_PATH}. "
                "Run `python scripts/train_model.py` from the repository root."
            )
            return

        try:
            self.model = self._load_artifact(MODEL_PATH)
            self._load_label_mapping()
        except Exception as exc:  # noqa: BLE001 - surface the concrete error in /health.
            self.model = None
            self.load_error = f"Could not load model artifact: {exc}"

    def predict(self, seconds: float, latitude: float, longitude: float) -> Dict[str, Any]:
        """Run one prediction using decimal coordinates without integer casting."""

        if not self.is_loaded:
            self.load()

        if not self.is_loaded:
            raise RuntimeError(self.load_error or "Model is not loaded.")

        features = pd.DataFrame(
            [[float(seconds), float(latitude), float(longitude)]],
            columns=FEATURE_NAMES,
        )
        raw_prediction = self.model.predict(features)[0]
        predicted_country = self._country_for_class(raw_prediction)

        return {
            "predicted_class_id": self._class_id_for_prediction(raw_prediction),
            "predicted_country": predicted_country,
            "probabilities": self._predict_probabilities(features),
        }

    def model_info(self) -> Dict[str, Any]:
        """Return model metadata for the `/model-info` endpoint."""

        if not self.is_loaded:
            self.load()

        model_type = self.model.__class__.__name__ if self.model is not None else None
        return {
            "model_type": model_type,
            "features": FEATURE_NAMES,
            "classes": self._country_labels(),
            "model_path": str(MODEL_PATH.relative_to(MODEL_PATH.parents[1])),
        }

    @staticmethod
    def _load_artifact(path: Any) -> Any:
        try:
            return joblib.load(path)
        except Exception:
            with open(path, "rb") as model_file:
                return pickle.load(model_file)

    def _load_label_mapping(self) -> None:
        self.class_id_to_country = {}
        self.class_labels = []

        if not LABEL_MAPPING_PATH.exists():
            return

        with open(LABEL_MAPPING_PATH, "r", encoding="utf-8") as mapping_file:
            mapping = json.load(mapping_file)

        if isinstance(mapping, dict) and "class_id_to_country" in mapping:
            self.class_id_to_country = {
                str(class_id): str(country)
                for class_id, country in mapping["class_id_to_country"].items()
            }
            self.class_labels = [str(country) for country in mapping.get("classes", [])]
            return

        if isinstance(mapping, dict) and "classes" in mapping:
            self.class_labels = [str(country) for country in mapping["classes"]]
            self.class_id_to_country = {
                str(index): country for index, country in enumerate(self.class_labels)
            }
            return

        if isinstance(mapping, dict):
            self.class_id_to_country = {
                str(class_id): str(country) for class_id, country in mapping.items()
            }
            self.class_labels = list(self.class_id_to_country.values())

    def _model_classes(self) -> List[Any]:
        if self.model is None:
            return []

        if hasattr(self.model, "classes_"):
            return list(self.model.classes_)

        named_steps = getattr(self.model, "named_steps", {})
        for step in reversed(list(named_steps.values())):
            if hasattr(step, "classes_"):
                return list(step.classes_)

        return []

    def _country_labels(self) -> List[str]:
        if self.class_labels:
            return self.class_labels

        labels = [self._country_for_class(class_value) for class_value in self._model_classes()]
        return labels

    def _class_key(self, class_value: Any) -> str:
        if isinstance(class_value, (int, np.integer)):
            return str(int(class_value))
        if isinstance(class_value, (float, np.floating)) and float(class_value).is_integer():
            return str(int(class_value))
        return str(class_value)

    def _country_for_class(self, class_value: Any) -> str:
        key = self._class_key(class_value)

        if key in self.class_id_to_country:
            return self.class_id_to_country[key]

        if self.class_labels:
            try:
                index = int(key)
            except ValueError:
                return key
            if 0 <= index < len(self.class_labels):
                return self.class_labels[index]

        return key

    def _class_id_for_prediction(self, class_value: Any) -> int:
        key = self._class_key(class_value)
        try:
            return int(key)
        except ValueError:
            pass

        for index, model_class in enumerate(self._model_classes()):
            if self._class_key(model_class) == key:
                return index

        return -1

    def _predict_probabilities(self, features: pd.DataFrame) -> Optional[Dict[str, float]]:
        if self.model is None or not hasattr(self.model, "predict_proba"):
            return None

        probabilities = self.model.predict_proba(features)[0]
        model_classes = self._model_classes()

        if not model_classes:
            model_classes = list(range(len(probabilities)))

        return {
            self._country_for_class(class_value): round(float(probability), 6)
            for class_value, probability in zip(model_classes, probabilities)
        }


@lru_cache(maxsize=1)
def get_model_service() -> ModelService:
    """Return the process-wide model service instance."""

    return ModelService()
