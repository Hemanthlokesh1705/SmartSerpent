from tensorflow.keras.models import load_model
from src.config.setting import base_model_path
def load_myModel():
    try:
        model=load_model(base_model_path)
        print(model.summary())
    except Exception as e:
        print(e)
load_myModel()
