# UFO Local Deployment Project

GitHub repository: <https://github.com/fyangmie/UFO>

Hugging Face Space: <https://huggingface.co/spaces/fyangmie/UFO>

Live demo URL: <https://huggingface.co/spaces/fyangmie/UFO>

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

The Streamlit frontend calls the FastAPI backend over HTTP. Streamlit does not load the model directly.

## Project Structure

```text
.
├── README.md
├── PRD.md
├── AGENTS.md
├── requirements.txt
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

## Hugging Face Spaces Docker Deployment

GitHub stores the code, but it does not run this FastAPI and Streamlit app by itself. The deployed classroom demo uses Hugging Face Spaces with the Docker SDK.

This repository includes a `Dockerfile` and `scripts/start_cloud.sh`. The container starts FastAPI on the internal local URL `http://127.0.0.1:8000` and exposes Streamlit on the Hugging Face Spaces public port `7860`.

For the Hugging Face Space:

1. Open <https://huggingface.co/spaces/fyangmie/UFO>.
2. Set the Space SDK to **Docker**.
3. Upload or sync this repository's files to the Space.
4. Wait for the Docker build to finish.
5. Open the Space URL and run a prediction.

The Docker container uses these defaults:

```text
PORT=7860
UFO_BACKEND_PORT=8000
UFO_BACKEND_URL=http://127.0.0.1:8000
```

## Optional Render Deployment

The repository also keeps `render.yaml` for Render. If using Render instead of Hugging Face Spaces, deploy from the GitHub repository and use `bash scripts/start_cloud.sh` as the start command.

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
2. Start the backend with `uvicorn backend.main:app --host 127.0.0.1 --port 8000`.
3. Open `http://localhost:8000/docs` and show `/health`.
4. Send a `/predict` request with `seconds=30`, `latitude=34.05`, `longitude=-118.25`.
5. Start Streamlit with `streamlit run frontend/streamlit_app.py`.
6. Load a sample preset and click **Predict Country**.
7. Show the predicted country, probability table, and raw JSON response.
8. Explain that the frontend and backend are separate local services.

## Troubleshooting

- If `/health` says the model is not loaded, run `python scripts/train_model.py` from the repository root and restart Uvicorn.
- If Streamlit says the backend is unavailable, make sure Uvicorn is running on `http://localhost:8000`.
- If validation fails, check that `seconds` is 1 to 60, latitude is -90 to 90, and longitude is -180 to 180.
- If a pickle version error appears, reinstall dependencies and regenerate the model with the training script.
- If you replace `data/ufos.csv` with the original dataset, keep the required columns: `duration (seconds)`, `country`, `latitude`, and `longitude`.

## Limitations

The included dataset is a small classroom sample so the repository can run locally even when the original dataset is not present. Replace it with the original UFO dataset for a more realistic assignment submission. Even with the original data, this model should be explained as an educational country classifier, not evidence about UFO sightings.
