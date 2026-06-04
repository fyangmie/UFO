"""Streamlit frontend that calls the FastAPI UFO backend over HTTP."""

import os
from typing import Any, Dict, Optional

import pandas as pd
import requests
import streamlit as st


DEFAULT_BACKEND_URL = os.getenv("UFO_BACKEND_URL", "http://localhost:8000")
REQUEST_TIMEOUT_SECONDS = 5

PRESETS = {
    "Manual entry": {"seconds": 30.0, "latitude": 34.05, "longitude": -118.25},
    "US - Los Angeles": {"seconds": 30.0, "latitude": 34.05, "longitude": -118.25},
    "UK - London": {"seconds": 22.0, "latitude": 51.5074, "longitude": -0.1278},
    "Canada - Toronto": {"seconds": 18.0, "latitude": 43.6532, "longitude": -79.3832},
    "Germany - Berlin": {"seconds": 14.0, "latitude": 52.52, "longitude": 13.405},
    "Australia - Sydney": {"seconds": 40.0, "latitude": -33.8688, "longitude": 151.2093},
}


def normalize_backend_url(url: str) -> str:
    return url.strip().rstrip("/")


def get_json(url: str) -> Optional[Dict[str, Any]]:
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None


def post_prediction(url: str, payload: Dict[str, float]) -> Dict[str, Any]:
    response = requests.post(url, json=payload, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()
    return response.json()


def apply_preset(name: str) -> None:
    preset = PRESETS[name]
    st.session_state["seconds"] = preset["seconds"]
    st.session_state["latitude"] = preset["latitude"]
    st.session_state["longitude"] = preset["longitude"]


st.set_page_config(page_title="UFO Country Predictor", page_icon="U", layout="centered")

st.markdown(
    """
    <style>
    .result-card {
        border: 1px solid #d5dde5;
        border-radius: 8px;
        padding: 1rem;
        background: #f7fbff;
    }
    .result-country {
        font-size: 2rem;
        font-weight: 700;
        margin: 0.25rem 0 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("UFO Country Predictor")
st.write(
    "This classroom local-deployment demo sends sighting duration and decimal "
    "coordinates to a FastAPI backend, then displays the predicted country from "
    "a saved scikit-learn model."
)

st.sidebar.header("Backend")
backend_url = normalize_backend_url(
    st.sidebar.text_input("FastAPI backend URL", value=DEFAULT_BACKEND_URL)
)

health = get_json(f"{backend_url}/health")
if health and health.get("model_loaded"):
    st.sidebar.success("Backend online. Model loaded.")
elif health:
    st.sidebar.warning("Backend online, but the model is not loaded.")
    if health.get("error"):
        st.sidebar.caption(health["error"])
else:
    st.sidebar.error("Backend unavailable. Start Uvicorn on port 8000.")

selected_preset = st.sidebar.selectbox("Sample preset", list(PRESETS.keys()))
if st.sidebar.button("Load preset"):
    apply_preset(selected_preset)

if "seconds" not in st.session_state:
    apply_preset("US - Los Angeles")

st.subheader("Sighting Inputs")
seconds = st.number_input(
    "Seconds",
    min_value=1.0,
    max_value=60.0,
    step=1.0,
    key="seconds",
)
latitude = st.number_input(
    "Latitude",
    min_value=-90.0,
    max_value=90.0,
    step=0.0001,
    format="%.4f",
    key="latitude",
)
longitude = st.number_input(
    "Longitude",
    min_value=-180.0,
    max_value=180.0,
    step=0.0001,
    format="%.4f",
    key="longitude",
)

payload = {
    "seconds": float(seconds),
    "latitude": float(latitude),
    "longitude": float(longitude),
}

st.map(pd.DataFrame([{"lat": latitude, "lon": longitude}]), zoom=4)

if st.button("Predict Country", type="primary"):
    try:
        result = post_prediction(f"{backend_url}/predict", payload)
    except requests.ConnectionError:
        st.error("Could not connect to the backend. Start it with `uvicorn backend.main:app --host 127.0.0.1 --port 8000`.")
    except requests.HTTPError as exc:
        detail = exc.response.text if exc.response is not None else str(exc)
        st.error(f"The backend returned an error: {detail}")
    except requests.RequestException as exc:
        st.error(f"Prediction request failed: {exc}")
    else:
        country = result.get("predicted_country", "Unknown")
        st.markdown(
            f"""
            <div class="result-card">
                <div>Likely country</div>
                <div class="result-country">{country}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        probabilities = result.get("probabilities")
        if probabilities:
            probability_df = (
                pd.DataFrame(
                    [{"Country": country, "Probability": probability} for country, probability in probabilities.items()]
                )
                .sort_values("Probability", ascending=False)
                .reset_index(drop=True)
            )
            st.subheader("Prediction Probabilities")
            st.dataframe(probability_df, use_container_width=True, hide_index=True)
            st.bar_chart(probability_df.set_index("Country"))

        with st.expander("Raw JSON response"):
            st.json(result)
