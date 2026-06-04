# PRD.md — UFO Project Local Deployment Workflow

> Target task: apply the 7-step local deployment workflow to the UFO Project: model training in Jupyter, FastAPI backend with Uvicorn, Streamlit frontend, and localhost integration.

---

## 1. Project Summary

Build a local machine-learning web application that predicts the likely country of a UFO sighting from three user inputs:

- `Seconds`: duration of the sighting in seconds
- `Latitude`: latitude of the sighting location
- `Longitude`: longitude of the sighting location

The original UFO project trains a scikit-learn Logistic Regression model on `ufos.csv`, serializes it as `ufo-model.pkl`, and serves predictions through a legacy Flask form app. For this classroom task, the goal is to upgrade the project to the local deployment architecture used in the course videos:

```text
Jupyter Notebook / training script
        ↓
Saved model artifact: ufo-model.pkl
        ↓
FastAPI backend served by Uvicorn
        ↓
Streamlit frontend
        ↓
Browser-based localhost demo
```

The final result should run locally with two services:

- Backend API: `http://localhost:8000`
- Frontend UI: `http://localhost:8501`

---

## 2. Background and Assignment Interpretation

The classroom task lists seven local-deployment videos:

1. Project demo / inspiration
2. Training models using Jupyter Notebooks
3. Interacting with trained models via Streamlit
4. Local deployment system architecture
5. Building the FastAPI backend and running it with Uvicorn
6. Designing the Streamlit frontend
7. Localhost integration demo

The UFO-specific requirement is: apply the same entire 7-step workflow to the UFO Project.

Therefore, simply running the old Flask app is not enough for a high score. The high-score version should demonstrate that the student understands service separation:

- model training is reproducible;
- model inference is exposed as an API;
- the UI calls the API instead of loading the model directly;
- backend and frontend can be started independently;
- the project has clear instructions, validation, and evidence of successful local integration.

---

## 3. Existing Inputs and Legacy Behavior

The supplied project materials include:

- `ufos.csv`: UFO sighting dataset with fields such as city, state, country, shape, duration, latitude, longitude, and comments.
- `notebook.ipynb`: notebook that selects `Seconds`, `Country`, `Latitude`, and `Longitude`, cleans the data, label-encodes the country, trains Logistic Regression, and saves `ufo-model.pkl`.
- `ufo-model.pkl`: pickled scikit-learn model artifact.
- Legacy Flask files:
  - `app.py`
  - `index.html`
  - `styles.css`
  - `requirements.txt`

The legacy app flow is:

```text
HTML form → Flask /predict route → load pickled model → return prediction text in HTML
```

The new target flow is:

```text
Streamlit input widgets → HTTP POST request → FastAPI /predict endpoint → JSON result → Streamlit display
```

---

## 4. Goals

### 4.1 Functional Goals

1. Reproduce or load the UFO classification model.
2. Provide a FastAPI backend that exposes prediction functionality.
3. Provide a Streamlit frontend that lets users enter seconds, latitude, and longitude.
4. Connect Streamlit to FastAPI over localhost.
5. Display readable country labels: `Australia`, `Canada`, `Germany`, `UK`, `US`.
6. Include a clear README with setup and run commands.
7. Include screenshots or written proof of successful local execution.

### 4.2 Learning Goals

The project should clearly show understanding of:

- the difference between training and inference;
- why a model is serialized using pickle/joblib;
- how a backend API receives request data and returns prediction JSON;
- how a frontend sends requests to a backend;
- how localhost ports work when two services run at once;
- why input validation matters in ML apps.

### 4.3 High-Score Goals

To improve beyond the baseline, implement the following:

- clean, professional folder structure;
- Pydantic request/response schemas;
- `/health`, `/model-info`, `/predict`, and optional `/batch-predict` endpoints;
- Streamlit sidebar with backend URL and sample presets;
- CSV batch upload prediction in Streamlit;
- visible API status check;
- user-friendly error messages;
- type-safe handling of decimal latitude/longitude;
- test file or smoke-test script;
- model card or short explanation of limitations;
- optional Docker files prepared for the next assignment task.

---

## 5. Non-Goals

For Task 1, the project does not need to be deployed to a cloud server.

For Task 1, the project does not need full Docker deployment, although Docker scaffolding may be included as a bonus.

The project is not intended to be a scientifically meaningful UFO predictor. The high reported accuracy mainly reflects the fact that latitude and longitude strongly indicate country.

---

## 6. User Stories

### Student / Developer

As a student, I want to run one command for the backend and one command for the frontend so that I can demonstrate local deployment in class.

### Demo User

As a demo user, I want to enter duration, latitude, and longitude, then see the predicted country and confidence/probability so that I understand what the model is doing.

### Teacher / Reviewer

As a reviewer, I want to see separated backend and frontend code, clear setup instructions, and working localhost integration so that I can verify the student completed the 7-step workflow.

---

## 7. Proposed Repository Structure

```text
ufo-local-deployment/
├── README.md
├── PRD.md
├── AGENTS.md                  # or AGENT.md if required by submission format
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
└── docs/
    ├── architecture.md
    └── screenshots/
```

If the current repository is smaller, Codex may create this structure and move existing files into the correct locations.

---

## 8. Detailed Requirements

### 8.1 Model Training / Model Artifact

Minimum requirement:

- Use the existing `ufo-model.pkl` if available.

Preferred high-score requirement:

- Add `scripts/train_model.py` that reproduces model training from `ufos.csv`:
  - load CSV;
  - select `duration (seconds)`, `country`, `latitude`, and `longitude`;
  - rename columns to `Seconds`, `Country`, `Latitude`, `Longitude`;
  - drop missing values;
  - filter `Seconds` to `[1, 60]`;
  - encode country labels;
  - train Logistic Regression;
  - save model to `models/ufo-model.pkl`;
  - save label mapping to `models/label_mapping.json`;
  - print classification report and accuracy.

Important implementation details:

- Accept decimal latitude and longitude.
- Do not cast latitude/longitude to integer.
- Use stable random seed, for example `random_state=0`.
- Use `max_iter=1000` or higher for Logistic Regression to reduce convergence warnings.

### 8.2 Backend: FastAPI + Uvicorn

Create `backend/main.py` with:

- FastAPI app initialization.
- Model loading at startup or through a cached function.
- Pydantic schemas for request and response.
- Validation for input ranges.
- JSON API endpoints.

Required endpoints:

#### `GET /`

Returns basic app information.

Example response:

```json
{
  "app": "UFO Country Predictor API",
  "status": "running",
  "docs": "/docs"
}
```

#### `GET /health`

Returns whether backend and model are available.

Example response:

```json
{
  "status": "ok",
  "model_loaded": true
}
```

#### `GET /model-info`

Returns useful metadata.

Example response:

```json
{
  "model_type": "LogisticRegression",
  "features": ["Seconds", "Latitude", "Longitude"],
  "classes": ["Australia", "Canada", "Germany", "UK", "US"]
}
```

#### `POST /predict`

Request body:

```json
{
  "seconds": 30,
  "latitude": 34.05,
  "longitude": -118.25
}
```

Response body:

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

The `probabilities` field should be returned only if the model supports `predict_proba`.

Optional endpoint:

#### `POST /batch-predict`

Accepts multiple records and returns a list of prediction results.

### 8.3 Frontend: Streamlit

Create `frontend/streamlit_app.py`.

Required UI elements:

- Title and short project explanation.
- Sidebar for backend URL, default `http://localhost:8000`.
- Backend health check display.
- Numeric inputs/sliders:
  - seconds: 1 to 60;
  - latitude: -90 to 90;
  - longitude: -180 to 180.
- Predict button.
- Display result clearly, for example: `Likely country: US`.
- Display probability table if provided by backend.
- Show raw JSON response inside an expandable section for debugging.

High-score UI features:

- sample preset buttons, e.g. US, UK, Canada examples;
- CSV upload for batch predictions;
- map visualization of the input coordinate;
- clear error messages if backend is not running;
- short explanation of why latitude/longitude are strong predictors.

### 8.4 Localhost Integration

The final local demo must use two separate commands.

Backend:

```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Frontend:

```bash
streamlit run frontend/streamlit_app.py
```

Expected URLs:

- FastAPI docs: `http://localhost:8000/docs`
- Streamlit UI: `http://localhost:8501`

The frontend must call the backend using HTTP requests, not by importing the backend model service directly.

---

## 9. Dependencies

Recommended `requirements.txt`:

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

Optional:

```text
plotly
pydeck
```

---

## 10. Validation and Error Handling

Backend should validate:

- `seconds >= 1` and `seconds <= 60`;
- `latitude >= -90` and `latitude <= 90`;
- `longitude >= -180` and `longitude <= 180`.

Frontend should handle:

- backend unavailable;
- invalid response;
- timeout;
- CSV missing required columns;
- model file missing.

Important correction from the legacy app:

- Do not parse every form value as `int`.
- Latitude and longitude are floats and should remain floats.

---

## 11. Acceptance Criteria

The task is complete when:

1. `pip install -r requirements.txt` succeeds.
2. `uvicorn backend.main:app --reload --port 8000` starts the backend.
3. `http://localhost:8000/docs` shows FastAPI Swagger docs.
4. `GET /health` returns a healthy status.
5. `POST /predict` returns a JSON prediction for valid input.
6. `streamlit run frontend/streamlit_app.py` starts the frontend.
7. Streamlit successfully calls FastAPI and displays the predicted country.
8. README explains setup, training, running, and troubleshooting.
9. A smoke test or pytest test verifies the backend prediction endpoint.
10. No hardcoded absolute local paths are required.

---

## 12. Suggested Demo Script

1. Open terminal 1 and run backend:

```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

2. Open browser at:

```text
http://localhost:8000/docs
```

3. Test `/predict` with:

```json
{
  "seconds": 30,
  "latitude": 34.05,
  "longitude": -118.25
}
```

4. Open terminal 2 and run frontend:

```bash
streamlit run frontend/streamlit_app.py
```

5. Enter the same values in Streamlit and click predict.
6. Show the predicted country and probability table.
7. Upload a sample CSV if batch prediction is implemented.
8. Explain the architecture:

```text
Streamlit does user interaction.
FastAPI does inference.
The pickled model stores learned parameters.
Uvicorn runs the API server locally.
```

---

## 13. High-Score Checklist

- [ ] Clean FastAPI backend with Pydantic schemas.
- [ ] Separate Streamlit frontend.
- [ ] Frontend calls backend through HTTP.
- [ ] Model training is reproducible through notebook or script.
- [ ] Model and label mapping are saved in `models/`.
- [ ] Input validation is implemented.
- [ ] `/docs`, `/health`, `/model-info`, and `/predict` work.
- [ ] Batch CSV prediction is implemented or documented as optional.
- [ ] README includes exact commands.
- [ ] Tests or smoke test included.
- [ ] Screenshots or demo notes included.
- [ ] Code handles decimal latitude/longitude correctly.
- [ ] Legacy Flask code is preserved only as reference or moved to `legacy/`.
- [ ] Optional Docker scaffolding is included for future Task 3.

---

## 14. Risks and Mitigations

### Risk: Model pickle version mismatch

Mitigation:

- Keep `scikit-learn` version consistent where possible.
- Provide `scripts/train_model.py` so the model can be regenerated.

### Risk: Frontend cannot connect to backend

Mitigation:

- Put backend URL in Streamlit sidebar.
- Add health check.
- Use timeout and clear error messages.

### Risk: Wrong country mapping

Mitigation:

- Save `label_mapping.json` from the fitted encoder.
- Do not rely only on a hardcoded list unless it matches the training encoder.

### Risk: Old Flask app passes only integers

Mitigation:

- Use `float` for latitude and longitude.
- Use Pydantic models in FastAPI.

---

## 15. Recommended Implementation Order for Codex

1. Inspect existing files.
2. Create project folder structure.
3. Move or copy data/model/notebook to appropriate folders.
4. Create backend schemas and model service.
5. Create FastAPI endpoints.
6. Create Streamlit frontend.
7. Update requirements.
8. Create README.
9. Add smoke test or pytest.
10. Run backend checks.
11. Run frontend checks manually where possible.
12. Summarize changes and commands.

