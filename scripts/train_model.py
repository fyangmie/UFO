"""Train and save the UFO country classifier from data/ufos.csv."""

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "ufos.csv"
MODEL_PATH = PROJECT_ROOT / "models" / "ufo-model.pkl"
LABEL_MAPPING_PATH = PROJECT_ROOT / "models" / "label_mapping.json"
FEATURES = ["Seconds", "Latitude", "Longitude"]

COLUMN_MAP = {
    "duration (seconds)": "Seconds",
    "country": "Country",
    "latitude": "Latitude",
    "longitude": "Longitude",
}

COUNTRY_LABELS = {
    "au": "Australia",
    "australia": "Australia",
    "ca": "Canada",
    "canada": "Canada",
    "de": "Germany",
    "germany": "Germany",
    "gb": "UK",
    "uk": "UK",
    "united kingdom": "UK",
    "us": "US",
    "usa": "US",
    "united states": "US",
}


def load_training_data() -> pd.DataFrame:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Could not find dataset at {DATA_PATH}")

    raw = pd.read_csv(DATA_PATH)
    missing_columns = [column for column in COLUMN_MAP if column not in raw.columns]
    if missing_columns:
        raise ValueError(f"Dataset is missing required columns: {missing_columns}")

    df = raw[list(COLUMN_MAP)].rename(columns=COLUMN_MAP)

    for column in ["Seconds", "Latitude", "Longitude"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df["Country"] = df["Country"].astype(str).str.strip()
    df = df.dropna(subset=["Seconds", "Country", "Latitude", "Longitude"])
    df = df[df["Seconds"].between(1, 60)]
    df["Country"] = (
        df["Country"]
        .str.lower()
        .map(COUNTRY_LABELS)
        .fillna(df["Country"])
    )

    if df.empty:
        raise ValueError("No usable rows remain after cleaning and filtering.")

    return df


def main() -> None:
    df = load_training_data()
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(df["Country"])
    x = df[FEATURES]

    if len(label_encoder.classes_) < 2:
        raise ValueError("Training requires at least two country classes.")

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.25,
        random_state=0,
        stratify=y,
    )

    model = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            ("classifier", LogisticRegression(max_iter=2000, random_state=0)),
        ]
    )
    model.fit(x_train, y_train)

    predictions = model.predict(x_test)
    accuracy = accuracy_score(y_test, predictions)

    print("Classification report:")
    print(classification_report(y_test, predictions, target_names=label_encoder.classes_))
    print(f"Accuracy: {accuracy:.3f}")

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    mapping = {
        "features": FEATURES,
        "classes": label_encoder.classes_.tolist(),
        "class_id_to_country": {
            str(class_id): country
            for class_id, country in enumerate(label_encoder.classes_.tolist())
        },
    }
    with open(LABEL_MAPPING_PATH, "w", encoding="utf-8") as mapping_file:
        json.dump(mapping, mapping_file, indent=2)

    print(f"Saved model to {MODEL_PATH.relative_to(PROJECT_ROOT)}")
    print(f"Saved label mapping to {LABEL_MAPPING_PATH.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
