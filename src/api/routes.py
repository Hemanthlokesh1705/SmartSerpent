from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.api.get_snake_info import SnakeInfoService
from src.llm.desgin_model import GeminiModel


BASE_DIR = Path(__file__).resolve().parents[2]
FRONTEND_DIR = BASE_DIR / "frontend"
TEMPLATES_DIR = FRONTEND_DIR / "templates"
STATIC_DIR = FRONTEND_DIR / "static"

router = APIRouter(prefix="/api")
snake_service = SnakeInfoService()
gemini_model = GeminiModel()


class DetailsRequest(BaseModel):
    snake_name: str
    confidence: float | None = None


def normalize_details(details: dict) -> dict:
    normalized = dict(details)
    normalized["habitat"] = normalized.get("habitat") or "Habitat information is not available for this result."
    normalized["venom_type"] = normalized.get("venom_type") or "Not available or not applicable."
    normalized["scientific_name"] = normalized.get("scientific_name") or "Unknown"
    normalized["canonical_name"] = normalized.get("canonical_name") or normalized.get("input_label") or "Unknown"
    normalized["confidence_note"] = (
        normalized.get("confidence_note")
        or "This detail set was generated with limited certainty. Please verify with trusted sources."
    )
    return normalized


@router.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/predict")
async def predict_snake(file: UploadFile = File(...)) -> dict:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Please upload an image file.")

    suffix = Path(file.filename).suffix or ".jpg"

    try:
        with NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            contents = await file.read()
            temp_file.write(contents)
            temp_path = Path(temp_file.name)

        result = snake_service.predict(temp_path)
        return result
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {exc}") from exc
    finally:
        if "temp_path" in locals() and temp_path.exists():
            temp_path.unlink(missing_ok=True)


@router.post("/details")
def snake_details(payload: DetailsRequest) -> dict:
    snake_name = payload.snake_name.strip()
    if not snake_name:
        raise HTTPException(status_code=400, detail="Snake name is required.")

    details = gemini_model.generate_output(snake_name)
    return {
        "snake_name": snake_name,
        "confidence": payload.confidence,
        "details": normalize_details(details.model_dump()),
    }


def create_app() -> FastAPI:
    app = FastAPI(
        title="SmartSerpent",
        description="Snake image prediction with Gemini-powered species details.",
        version="1.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router)
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.get("/", include_in_schema=False)
    def landing_page() -> FileResponse:
        return FileResponse(TEMPLATES_DIR / "index.html")

    @app.get("/predict", include_in_schema=False)
    def predict_page() -> FileResponse:
        return FileResponse(TEMPLATES_DIR / "predict.html")

    @app.get("/details", include_in_schema=False)
    def details_page() -> FileResponse:
        return FileResponse(TEMPLATES_DIR / "details.html")

    return app
