from pathlib import Path


def root_dir() -> Path:
    return Path(__file__).parent.parent


def load_file(path: Path) -> str:
    with open(path, "r") as fh:
        file_data = fh.read()
    return file_data
