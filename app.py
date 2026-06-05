"""Hugging Face Spaces Gradio frontend for the UFO country predictor."""

import gradio as gr

from model_service import predict_country


SAMPLES = [
    [30, 34.0522, -118.2437],
    [22, 51.5074, -0.1278],
    [18, 43.6532, -79.3832],
    [14, 52.5200, 13.4050],
    [40, -33.8688, 151.2093],
]


with gr.Blocks(title="UFO Country Demo") as demo:
    gr.Markdown("# UFO Country Predictor")
    gr.Markdown(
        "Gradio demo for predicting the likely UFO sighting country from "
        "duration, latitude, and longitude."
    )

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
        predict_country,
        inputs=[seconds, latitude, longitude],
        outputs=[country, confidence, probabilities],
        api_name="predict_country",
    )


if __name__ == "__main__":
    demo.launch(show_error=True)
