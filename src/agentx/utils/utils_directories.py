from pathlib import Path

def is_file_exists(path: str | Path) -> bool:
    return Path(path).is_file()

def is_directory_exists(directory: str):
    return Path(directory).is_dir()
