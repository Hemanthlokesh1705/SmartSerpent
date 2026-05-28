from pathlib import Path
import pickle

from src.config.setting import faiss_index_path,snake_labels
from src.retrive.embedding_manger import EmbeddingManager


embedding_manager=EmbeddingManager()
snake_labels_path=Path(snake_labels)


def load_snake_labels():

    if not snake_labels_path.exists():
        raise FileNotFoundError(
            "snake_labels.pkl not found. Build the FAISS index and metadata first."
        )

    with open(
        snake_labels_path,
        "rb"
    ) as file:
        return pickle.load(
            file
        )


def get_snake_name(
    img_path:str
):

    embedding=embedding_manager.generate_embedding(
        img_path
    )

    index=embedding_manager.load_index(
        faiss_index_path
    )

    snake_labels=load_snake_labels()

    similarity,snake_indices=embedding_manager.search(
        embedding,
        index=index
    )

    snake_index=int(
        snake_indices[0][0]
    )

    return {
        "snake_name": snake_labels[snake_index],
        "similarity": float(
            similarity[0][0]
        ),
        "index": snake_index,
    }
