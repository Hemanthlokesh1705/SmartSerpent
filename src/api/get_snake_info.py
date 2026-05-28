from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import HTTPException
from PIL import Image

from src.retrive.get_snake import get_snake_name
from src.utils.snake_prediction import SnakePredictor


class SnakeInfoService:
    def __init__(self) -> None:
        self.predictor = SnakePredictor()

    def _upscale_image(self, image_path: str) -> str:
        source_path = Path(image_path)

        with Image.open(source_path) as img:
            width, height = img.size
            upscaled = img.resize((width * 2, height * 2), Image.Resampling.BICUBIC)

            suffix = source_path.suffix or ".jpg"
            with NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                temp_path = temp_file.name

            upscaled.save(temp_path)

        return temp_path

    def predict(self, image_path: str | Path) -> dict:
        image_path = str(image_path)
        upscaled_image_path = None

        try:
            upscaled_image_path = self._upscale_image(image_path)
            try:
                baseline_prediction = self.predictor.predict(upscaled_image_path)
            except Exception as exc:
                raise HTTPException(
                    status_code=500,
                    detail=f"Base model prediction failed: {exc}",
                ) from exc

            similarity_prediction = None
            try:
                similarity_prediction = get_snake_name(upscaled_image_path)
            except Exception:
                similarity_prediction = None

            primary_name = baseline_prediction["snake_name"]
            primary_confidence = baseline_prediction["confidence"]

            if similarity_prediction and similarity_prediction["similarity"] > 0.85:
                primary_name = similarity_prediction["snake_name"]
                primary_confidence = round(similarity_prediction["similarity"] * 100, 2)

            return {
                "snake_name": primary_name,
                "confidence": primary_confidence,
                "baseline_prediction": baseline_prediction,
                "similarity_prediction": similarity_prediction,
            }
        finally:
            if upscaled_image_path:
                Path(upscaled_image_path).unlink(missing_ok=True)
