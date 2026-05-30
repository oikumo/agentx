import os
import time
import datetime
import shutil
import warnings
from pathlib import Path


def safe_int(value: str) -> int | None:
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def clear_console():
    if os.name == "nt":
        _ = os.system("cls")
    else:
        _ = os.system("clear")


def create_directory_with_timestamp(name: str, base_directory) -> str | None:
    now = datetime.datetime.now()
    datetime_string = now.strftime("%Y-%m-%d-%H-%M-%S")
    directory = f"{name}_{datetime_string}"
    session_directory = f"{base_directory}/{directory}"
    
    if os.path.isdir(session_directory):
        print("error file exists")
        return None
    
    directory_path = Path(session_directory)
    
    try:
        directory_path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print("create directory error")
        return None
    
    if not os.path.isdir(session_directory):
        print("error checking if directory exits")
        return None
    
    return str(directory_path.absolute().resolve())


def create_directory_without_timestamp(name: str, base_directory) -> str | None:
    """Create a directory without timestamp (for current session)."""
    directory = f"{name}"
    session_directory = f"{base_directory}/{directory}"
    
    directory_path = Path(session_directory)
    
    try:
        directory_path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print("create directory error")
        return None
    
    if not os.path.isdir(session_directory):
        print("error checking if directory exits")
        return None
    
    return str(directory_path.absolute().resolve())

def file_exists(path: str | Path) -> bool:
    return Path(path).is_file()

def directory_exists(directory: str):
    return os.path.isdir(directory)

def get_directories_start_with(base_directory: str, prefix: str) -> list[Path]:
    if not directory_exists(base_directory):
        return []

    base_path = Path(base_directory)
    directories = [d for d in base_path.iterdir() if d.is_dir() and d.name.startswith(prefix)]

    return directories


def save_to_output(text: str):
    with open("local/output.txt", "w") as file:
        file.write(text)


def is_directory_allowed_to_deletion(directory_path: str) -> bool:
    from agentx.utils.security import DIRECTORIES_DELETION_ALLOWED

    if not DIRECTORIES_DELETION_ALLOWED:
        raise PermissionError(
            f"trying to delete a directory but filter is empty, Directory: {directory_path}"
        )

    current_directory: Path = Path.cwd()
    candidate_directory_path: Path = Path(directory_path)

    try:
        candidate_directory_path.is_relative_to(current_directory)
    except Exception as e:
        print(e)
        raise PermissionError(
            f"trying to delete a directory when is out of current directory. Directory: {directory_path}"
        )

    allowed_directories = []
    for directory_allowed in DIRECTORIES_DELETION_ALLOWED:
        allowed_directory = current_directory / directory_allowed
        allowed_directories.append(allowed_directory)

    for allowed_directory in allowed_directories:
        try:
            candidate_directory_path.relative_to(allowed_directory)
            return True
        except Exception:
            pass

    raise PermissionError(
        f"trying to delete a directory not allowed for deletion. Directory: {directory_path}"
    )


def dangerous_delete_directory(directory_path: str) -> bool:
    warnings.warn(
        "This function dangerous_delete_directory() is potentially dangerous and should be used with caution, especially with untrusted input.",
        UserWarning,
        stacklevel=2,
    )

    if not is_directory_allowed_to_deletion(directory_path):
        return False

    if not os.path.isdir(directory_path):
        print(f"Directory not found or is not a directory: {directory_path}")
        return False

    shutil.rmtree(directory_path)
    print(f"Permanently deleted directory: {directory_path}")

    return True
