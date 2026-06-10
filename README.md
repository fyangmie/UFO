---
title: UFO Country Demo
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
---

# UFO Local Deployment Project

GitHub repository: <https://github.com/fyangmie/UFO>

Hugging Face Space: <https://huggingface.co/spaces/fyangmie/UFO>

Live demo URL: <https://fyangmie-ufo.hf.space>

Hugging Face project page: <https://huggingface.co/spaces/fyangmie/UFO>

This project demonstrates a clean local deployment workflow for a classroom UFO country classifier. A scikit-learn model predicts the likely sighting country from three inputs:

- `seconds`
- `latitude`
- `longitude`

This is an educational classifier for learning local ML deployment. It is not a scientific UFO predictor; the model mostly learns that latitude and longitude correspond to country regions.

## Architecture

```text
Jupyter Notebook or training script
        |
        v
saved scikit-learn model artifact
        |
        v
FastAPI backend served by Uvicorn
        |
        v
Streamlit frontend
        |
        v
localhost browser demo
```

The local classroom architecture keeps Streamlit and FastAPI separate.

The Docker deployment keeps the same backend separation while exposing a Gradio page that matches the teacher's example Space style:

```text
Browser
   |
   v
Gradio frontend on port 7860
   |
   | HTTP request
   v
FastAPI backend on 127.0.0.1:8000
   |
   v
models/ufo-model.pkl
```

Only port `7860` is public. FastAPI remains internal to the container, and the Gradio frontend does not load the model directly.

## Project Structure

```text
.
├── README.md
├── PRD.md
├── AGENTS.md
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── app.py
├── model_service.py
├── data/ufos.csv
├── notebooks/notebook.ipynb
├── models/ufo-model.pkl
├── models/label_mapping.json
├── backend/
├── frontend/
├── scripts/
├── tests/
└── legacy/
```

## Setup

Create and activate a virtual environment if desired, then install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Train Or Regenerate The Model

```bash
python scripts/train_model.py
```

The script:

- loads `data/ufos.csv`
- renames `duration (seconds)`, `country`, `latitude`, and `longitude`
- converts numeric fields safely
- filters `Seconds` to 1 through 60
- trains Logistic Regression
- saves `models/ufo-model.pkl`
- saves `models/label_mapping.json`

## Run The Backend

```bash
uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Open the API docs at:

```text
http://localhost:8000/docs
```

Useful endpoints:

- `GET /`
- `GET /health`
- `GET /model-info`
- `POST /predict`

## Run The Frontend

In a second terminal:

```bash
streamlit run frontend/streamlit_app.py
```

Open the app at the local URL printed by Streamlit, usually:

```text
http://localhost:8501
```

## Build And Run With Docker

Build the image from the repository root:

```bash
docker build -t ufo-country-demo .
```

Run the container:

```bash
docker run --rm -p 7860:7860 --name ufo-country-demo ufo-country-demo
```

Open:

```text
http://localhost:7860
```

The container starts both services:

- FastAPI: internal `http://127.0.0.1:8000`
- Gradio: public `http://0.0.0.0:7860`

Stop the running container with `Ctrl+C`, or from another terminal:

```bash
docker stop ufo-country-demo
```

Inspect logs to demonstrate the Gradio-to-FastAPI HTTP requests:

```bash
docker logs ufo-country-demo
```

## Hugging Face Spaces Docker Deployment

GitHub stores the code, but it does not run the app by itself. The public classroom demo uses a Hugging Face Docker Space while retaining a Gradio interface similar to the teacher examples:

- <https://huggingface.co/spaces/endsieg97/mnist-digit-demo>
- <https://huggingface.co/spaces/endsieg97/ufo-country-demo>

The Space configuration is defined in this README:

```yaml
sdk: docker
app_port: 7860
```

Hugging Face builds the root `Dockerfile`, runs `scripts/start_cloud.sh`, exposes port `7860`, and leaves FastAPI reachable only inside the container.

The Gradio interface exposes a callable action named:

```text
/predict_country
```

Deployment:

1. Open <https://huggingface.co/spaces/fyangmie/UFO>.
2. Confirm the README metadata shows `sdk: docker`.
3. Push the repository files to the Space.
4. Wait for the Docker build and health check to pass.
5. Open <https://fyangmie-ufo.hf.space> and run a prediction.

## Example API Request

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"seconds": 30, "latitude": 34.05, "longitude": -118.25}'
```

Example response:

```json
{
  "predicted_class_id": 4,
  "predicted_country": "US",
  "probabilities": {
    "Australia": 0.01,
    "Canada": 0.02,
    "Germany": 0.01,
    "UK": 0.03,
    "US": 0.93
  }
}
```

## Smoke Test And Pytest

With the backend running:

```bash
python scripts/smoke_test.py
```

Run automated backend tests:

```bash
pytest -q
```

## Classroom Demo Script

1. Run `python scripts/train_model.py`.
2. Build the image with `docker build -t ufo-country-demo .`.
3. Run it with `docker run --rm -p 7860:7860 --name ufo-country-demo ufo-country-demo`.
4. Open `http://localhost:7860`.
5. Load a sample coordinate and click **Predict**.
6. Show the predicted country, confidence, and probabilities.
7. Run `docker logs ufo-country-demo` and point out the FastAPI `/health` and `/predict` requests.
8. Open <https://fyangmie-ufo.hf.space> to demonstrate the same container in the cloud.
9. Explain that Docker standardizes the Python version, dependencies, model files, startup commands, and ports.

## Troubleshooting

- If `/health` says the model is not loaded, run `python scripts/train_model.py` from the repository root and restart Uvicorn.
- If Streamlit says the backend is unavailable, make sure Uvicorn is running on `http://localhost:8000`.
- If the Docker page says the backend is unavailable, inspect `docker logs ufo-country-demo`; the startup script waits for `/health` before launching Gradio.
- If port `7860` is already in use, run with another host port, for example `docker run --rm -p 7861:7860 ufo-country-demo`.
- If Hugging Face still treats the Space as Gradio SDK, confirm the README YAML says `sdk: docker`, then restart the Space.
- If validation fails, check that `seconds` is 1 to 60, latitude is -90 to 90, and longitude is -180 to 180.
- If a pickle version error appears, reinstall dependencies and regenerate the model with the training script.
- If you replace `data/ufos.csv` with the original dataset, keep the required columns: `duration (seconds)`, `country`, `latitude`, and `longitude`.

## Limitations

The included dataset is a small classroom sample so the repository can run locally even when the original dataset is not present. Replace it with the original UFO dataset for a more realistic assignment submission. Even with the original data, this model should be explained as an educational country classifier, not evidence about UFO sightings.
