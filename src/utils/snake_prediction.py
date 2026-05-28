import json
from pathlib import Path

import numpy as np
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

from src.config.setting import base_model_path, mapping_file_path


class SnakePredictor:
    def __init__(self) -> None:
        self.model = None
        self.class_mapping = None
        self._load_model()
        self._load_mapping()

    def _load_model(self) -> None:
        self.model = load_model(base_model_path)

    def _load_mapping(self) -> None:
        with open(mapping_file_path, "r", encoding="utf-8") as file:
            self.class_mapping = json.load(file)

    def predict(self, img_path: str | Path) -> dict:
        img = image.load_img(img_path, target_size=(356, 356))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)

        predictions = self.model.predict(img_array, verbose=0)
        class_index = int(np.argmax(predictions[0]))
        confidence = float(predictions[0][class_index]) * 100
        snake_name = self.class_mapping[str(class_index)]

        return {
            "snake_name": snake_name,
            "confidence": round(confidence, 2),
            "class_index": class_index,
        }
