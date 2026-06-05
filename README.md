---
title: UFO Country Demo
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 6.10.0
app_file: app.py
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

The local classroom architecture keeps Streamlit and FastAPI separate. The Hugging Face Space uses a small Gradio `app.py` at the repository root so the public website matches the teacher's example Space structure.

## Project Structure

```text
.
├── README.md
├── PRD.md
├── AGENTS.md
├── requirements.txt
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

## Hugging Face Spaces Gradio Deployment

GitHub stores the code, but it does not run the app by itself. The public classroom demo uses Hugging Face Spaces with the Gradio SDK, matching the teacher-style examples:

- <https://huggingface.co/spaces/endsieg97/mnist-digit-demo>
- <https://huggingface.co/spaces/endsieg97/ufo-country-demo>

The Space entrypoint is:

```text
app.py
```

The Gradio app exposes a callable endpoint:

```text
/predict_country
```

For the Hugging Face Space settings:

1. Open <https://huggingface.co/spaces/fyangmie/UFO>.
2. Set the Space SDK to **Gradio**.
3. Use `app.py` as the app file.
4. Upload or sync this repository's files to the Space.
5. Open the Space URL and run a prediction.

## Optional Docker Deployment

The repository also keeps `Dockerfile`, `render.yaml`, and `scripts/start_cloud.sh` for the earlier FastAPI + Streamlit cloud deployment path. Use the Gradio Space path above when matching the teacher example website structure.

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
