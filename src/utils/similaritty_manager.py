from src.retrive.embedding_manger import EmbeddingManager
from src.retrive.extract_image_paths import generate_file_path
from src.config.setting import dataset_path,image_path,snake_labels
import pickle


# Create object
manager = EmbeddingManager()

# Extract paths and labels
image_paths, snake_labels = generate_file_path(
    dataset_path
)

embeddings=[]
successful_image_paths=[]
successful_snake_labels=[]

for path, label in zip(
    image_paths,
    snake_labels
):

    try:

        emb=manager.generate_embedding(
            path
        )

        embeddings.append(
            emb
        )

        successful_image_paths.append(
            path
        )

        successful_snake_labels.append(
            label
        )

        print(
            f"Processed: {path}"
        )

    except Exception as e:

        print(
            f"Failed {path}: {e}"
        )


# Create FAISS index
index=manager.create_faiss_index(
    embeddings
)

# Save FAISS index
manager.save_index(
    index
)

# Save metadata
with open(
    snake_labels,
    "wb"
) as f:

    pickle.dump(
        successful_snake_labels,
        f
    )


with open(
    image_path,
    "wb"
) as f:

    pickle.dump(
        successful_image_paths,
        f
    )

print(
    "Everything saved successfully!"
)
