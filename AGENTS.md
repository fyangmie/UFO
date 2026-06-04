# AGENT.md — Codex Instructions for UFO Local Deployment Project

> Note: Codex officially auto-loads repository guidance from `AGENTS.md`. If this file is named `AGENT.md` for submission, also copy or rename it to `AGENTS.md` in the repository root before running Codex.

---

## 1. Mission

You are helping complete a classroom machine-learning web app task. Build a high-quality local deployment version of the UFO Project using:

- Jupyter Notebook or training script for model training;
- FastAPI backend served by Uvicorn;
- Streamlit frontend;
- localhost integration between frontend and backend.

The project must demonstrate the full local deployment workflow, not just a monolithic Flask app.

---

## 2. Context

The supplied legacy UFO project includes:

- `ufos.csv`: UFO sightings dataset.
- `notebook.ipynb`: model training notebook.
- `ufo-model.pkl`: pickled Logistic Regression model.
- `app.py`, `index.html`, `styles.css`, `requirements.txt`: legacy Flask web app.

The legacy Flask app predicts a country from:

- seconds;
- latitude;
- longitude.

The course task asks us to apply the local deployment workflow to the UFO project. Therefore, the final architecture must separate frontend and backend:

```text
Streamlit frontend → HTTP request → FastAPI backend → scikit-learn model → JSON response → Streamlit display
```

---

## 3. Expected Final Repository Structure

Create or normalize the repository to this structure:

```text
.
├── README.md
├── PRD.md
├── AGENTS.md
├── requirements.txt
├── data/
│   └── ufos.csv
├── notebooks/
│   └── notebook.ipynb
├── models/
│   ├── ufo-model.pkl
│   └── label_mapping.json
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── schemas.py
│   ├── model_service.py
│   └── config.py
├── frontend/
│   └── streamlit_app.py
├── scripts/
│   ├── train_model.py
│   └── smoke_test.py
├── tests/
│   └── test_backend.py
└── legacy/
    ├── app.py
    ├── templates/index.html
    └── static/css/styles.css
```

If the existing repository already has some files, preserve them where sensible and move legacy Flask code into `legacy/` rather than deleting it.

---

## 4. Hard Requirements

### Backend

Implement a FastAPI app in `backend/main.py`.

Required endpoints:

- `GET /` — basic app information.
- `GET /health` — status and model-loaded check.
- `GET /model-info` — model type, features, classes.
- `POST /predict` — accepts `seconds`, `latitude`, `longitude`; returns predicted country.

Use Pydantic schemas in `backend/schemas.py`.

Input validation:

- `seconds`: float or int, range 1 to 60.
- `latitude`: float, range -90 to 90.
- `longitude`: float, range -180 to 180.

Important: do not convert latitude and longitude to integers. Decimal coordinates are valid and should be preserved.

### Frontend

Implement a Streamlit app in `frontend/streamlit_app.py`.

Required UI:

- title and assignment description;
- sidebar backend URL, default `http://localhost:8000`;
- backend health check;
- input widgets for seconds, latitude, longitude;
- predict button;
- result card displaying predicted country;
- optional probability table if backend returns probabilities;
- expandable raw JSON response;
- clear error message if backend is unavailable.

### Model

Use `models/ufo-model.pkl` if present.

Also provide `scripts/train_model.py` so the model can be regenerated from `data/ufos.csv`.

The training script should:

1. load `data/ufos.csv`;
2. create a dataframe with `Seconds`, `Country`, `Latitude`, `Longitude`;
3. drop missing values;
4. filter `Seconds` to 1–60;
5. encode countries;
6. train Logistic Regression with `max_iter=1000` or greater;
7. save `models/ufo-model.pkl`;
8. save `models/label_mapping.json`;
9. print evaluation metrics.

### Requirements

Update `requirements.txt` to include:

```text
fastapi
uvicorn[standard]
streamlit
requests
pandas
numpy
scikit-learn
joblib
pydantic
pytest
httpx
```

Optional visualization dependencies are allowed if used, but avoid unnecessary complexity.

---

## 5. Quality Requirements

- Use clear module boundaries: API logic, schema definitions, and model loading should not all be tangled in one giant file if avoidable.
- Use robust relative paths with `pathlib.Path`.
- Avoid hardcoded absolute paths.
- Add docstrings and comments where they clarify the educational purpose.
- Keep code easy for a beginner to explain in class.
- Do not store secrets or API keys.
- Do not make network calls except from Streamlit to the local FastAPI backend.
- Do not silently swallow errors; show meaningful messages.
- Avoid changing model behavior unless necessary for correctness.

---

## 6. API Contract

### Request

`POST /predict`

```json
{
  "seconds": 30,
  "latitude": 34.05,
  "longitude": -118.25
}
```

### Response

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

If probabilities are unavailable, return `probabilities: null` or omit it consistently.

---

## 7. Testing and Verification

After making changes, run these checks where possible:

```bash
python -m pip install -r requirements.txt
python scripts/train_model.py
uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

In another terminal:

```bash
python scripts/smoke_test.py
streamlit run frontend/streamlit_app.py
```

If `pytest` tests are implemented:

```bash
pytest -q
```

The smoke test should send a JSON request to `http://localhost:8000/predict` and print the response.

---

## 8. README Requirements

Create or update `README.md` with:

1. project overview;
2. architecture diagram in text or Mermaid;
3. setup instructions;
4. model training instructions;
5. backend run command;
6. frontend run command;
7. example API request;
8. troubleshooting section;
9. classroom demo script;
10. explanation of why this is not a scientific UFO predictor.

---

## 9. High-Score Enhancements

Implement as many as reasonable without making the project fragile:

- `/model-info` endpoint.
- CSV batch prediction in Streamlit.
- sample preset values.
- map visualization of the selected coordinate.
- probability table.
- `tests/test_backend.py`.
- `scripts/smoke_test.py`.
- `docs/architecture.md`.
- screenshots folder or instructions for screenshots.
- optional Dockerfile and docker-compose.yml, clearly marked as bonus/future Task 3.

---

## 10. Do-Not Rules

- Do not submit only the old Flask app.
- Do not make Streamlit load the model directly as the main path; it must call FastAPI.
- Do not cast latitude/longitude to int.
- Do not remove the notebook unless it is moved to `notebooks/`.
- Do not hide errors by returning fake predictions.
- Do not require cloud deployment for Task 1.
- Do not use absolute paths that only work on one computer.

---

## 11. Completion Definition

The task is complete when:

- backend starts on `http://localhost:8000`;
- FastAPI docs are visible at `http://localhost:8000/docs`;
- `/health` confirms the model is loaded;
- `/predict` returns a country for valid input;
- Streamlit starts on `http://localhost:8501`;
- Streamlit prediction calls the backend over HTTP;
- README explains all commands clearly;
- code is clean enough for a beginner student to explain in class.

---

## 12. Final Response Expected from Codex

When finished, summarize:

1. files created or changed;
2. how to install dependencies;
3. how to train or regenerate the model;
4. how to run backend;
5. how to run frontend;
6. how to test prediction;
7. any limitations or remaining manual steps.

