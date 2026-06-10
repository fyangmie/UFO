"""Hugging Face Spaces Gradio frontend for the UFO country predictor."""

import os

import gradio as gr

from model_service import BackendClientError, backend_health, predict_country


SAMPLES = [
    [30, 34.0522, -118.2437],
    [22, 51.5074, -0.1278],
    [18, 43.6532, -79.3832],
    [14, 52.5200, 13.4050],
    [40, -33.8688, 151.2093],
]


def check_backend_status() -> str:
    """Render backend and model availability without hiding API errors."""

    try:
        backend_health()
    except BackendClientError as exc:
        return f"**Backend status:** unavailable - {exc}"
    return "**Backend status:** online, model loaded"


def call_api(seconds: float, latitude: float, longitude: float):
    """Convert API client failures into readable Gradio errors."""

    try:
        return predict_country(seconds, latitude, longitude)
    except BackendClientError as exc:
        raise gr.Error(str(exc)) from exc


with gr.Blocks(title="UFO Country Demo") as demo:
    gr.Markdown("# UFO Country Predictor")
    gr.Markdown(
        "Docker-deployed Gradio frontend that calls a FastAPI model backend "
        "over HTTP."
    )
    backend_status = gr.Markdown("**Backend status:** checking...")

    with gr.Row():
        seconds = gr.Slider(1, 60, value=30, step=1, label="Duration in seconds")
        latitude = gr.Number(value=34.0522, label="Latitude")
        longitude = gr.Number(value=-118.2437, label="Longitude")

    with gr.Row():
        country = gr.Textbox(label="Predicted country")
        confidence = gr.Number(label="Confidence")

    probabilities = gr.Label(label="Top probabilities")

    gr.Examples(
        examples=SAMPLES,
        inputs=[seconds, latitude, longitude],
        label="Sample sightings",
    )

    gr.Button("Predict").click(
        call_api,
        inputs=[seconds, latitude, longitude],
        outputs=[country, confidence, probabilities],
        api_name="predict_country",
    )
    demo.load(check_backend_status, outputs=backend_status)


if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=int(os.getenv("PORT", "7860")),
        show_error=True,
    )
