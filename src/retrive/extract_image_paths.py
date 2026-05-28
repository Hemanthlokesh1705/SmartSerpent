from pathlib import Path

def generate_file_path(folder_path: str):

    snake_labels = []
    image_paths = []

    ALLOWED_EXTENSIONS = {
        ".png",
        ".jpeg",
        ".jpg",
        ".webp"
    }

    folder = Path(folder_path)

    if not folder.exists():
        raise FileNotFoundError(
            f"{folder_path} does not exist"
        )

    for class_folder in sorted(folder.iterdir()):

        if class_folder.is_dir():

            snake_name = class_folder.name

            for img_path in sorted(class_folder.glob("*")):

                if img_path.suffix.lower() in ALLOWED_EXTENSIONS:

                    snake_labels.append(snake_name)

                    image_paths.append(
                        str(img_path)
                    )

    return image_paths, snake_labels