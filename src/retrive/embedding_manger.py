from tensorflow.keras.models import load_model, Model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from src.config.setting import base_model_path,faiss_index_path
import numpy as np
import faiss
from pathlib import Path


class EmbeddingManager:

    def __init__(self):
        self.model = None
        self.embedding_model = None
        self.load_pretrained_model()

    def load_pretrained_model(self):

        try:
            self.model = load_model(base_model_path)

            self.embedding_model = Model(
                inputs=self.model.input,
                outputs=self.model.layers[-2].output
            )

            print("Model loaded successfully!")

        except Exception as e:
            print("Error loading model:", e)

    def generate_embedding(
        self,
        img_path
    ) -> np.ndarray:

        img = image.load_img(
            img_path,
            target_size=(356,356)
        )

        img = image.img_to_array(img)

        img = np.expand_dims(
            img,
            axis=0
        )

        img = preprocess_input(img)

        embedding = self.embedding_model.predict(
            img,
            verbose=0
        )

        return embedding.flatten().astype(
            "float32"
        )

    def create_faiss_index(
        self,
        embeddings
    ):

        embeddings=np.array(
            embeddings,
            dtype="float32"
        )

        if embeddings.size == 0:
            raise ValueError(
                "No embeddings were generated. Check the dataset path and image preprocessing."
            )

        if embeddings.ndim == 1:
            embeddings=np.expand_dims(
                embeddings,
                axis=0
            )

        if embeddings.ndim != 2:
            raise ValueError(
                f"Embeddings must be a 2D array, got shape {embeddings.shape}."
            )

        faiss.normalize_L2(
            embeddings
        )

        dimension=embeddings.shape[1]

        index=faiss.IndexFlatIP(
            dimension
        )

        index.add(
            embeddings
        )

        return index

    def save_index(
        self,
        index,
        path=faiss_index_path
    ):

        faiss.write_index(
            index,
            path
        )

    def load_index(
        self,
        path=faiss_index_path
    ):

        if not Path(path).exists():
            raise FileNotFoundError(
                f"FAISS index not found at {path}. Build the index before searching."
            )

        return faiss.read_index(
            path
        )

    def search(
        self,
        query_embedding,
        index=faiss_index_path,
        k=1
    ):

        if isinstance(
            index,
            str
        ):
            index=self.load_index(
                index
            )

        query_embedding=np.expand_dims(
            query_embedding,
            axis=0
        )

        faiss.normalize_L2(
            query_embedding
        )

        distances,indices=index.search(
            query_embedding,
            k
        )

        return distances,indices
