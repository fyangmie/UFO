"""FastAPI entrypoint for the UFO Country Predictor backend."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from .config import APP_NAME
from .model_service import get_model_service
from .schemas import HealthResponse, ModelInfoResponse, PredictionRequest, PredictionResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the model once when Uvicorn starts the API process."""

    get_model_service().load()
    yield


app = FastAPI(
    title=APP_NAME,
    description="Educational FastAPI backend for local UFO country prediction.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
def read_root() -> dict:
    return {
        "app": APP_NAME,
        "status": "running",
        "docs": "/docs",
        "health": "/health",
        "predict": "/predict",
    }


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    service = get_model_service()
    service.load()
    status = "ok" if service.is_loaded else "error"
    return HealthResponse(
        status=status,
        model_loaded=service.is_loaded,
        error=service.load_error,
    )


@app.get("/model-info", response_model=ModelInfoResponse)
def model_info() -> ModelInfoResponse:
    service = get_model_service()
    info = service.model_info()
    return ModelInfoResponse(**info)


@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest) -> PredictionResponse:
    service = get_model_service()
    try:
        result = service.predict(
            seconds=request.seconds,
            latitude=request.latitude,
            longitude=request.longitude,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return PredictionResponse(**result)
