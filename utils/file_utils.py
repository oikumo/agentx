import datetime
import os
import shutil
import warnings
from pathlib import Path

from security.security import is_directory_allowed_to_deletion


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

def directory_exists(directory: str):
    return os.path.isdir(directory)

def dangerous_delete_directory(directory_path: str) -> bool:
    warnings.warn("This function dangerous_delete_directory() is potentially dangerous and should be used with caution, especially with untrusted input.",
        UserWarning, stacklevel=2)

    if not is_directory_allowed_to_deletion(directory_path):
        return False

    if not os.path.isdir(directory_path):
        print(f"Directory not found or is not a directory: {directory_path}")
        return False

    shutil.rmtree(directory_path)
    print(f"Permanently deleted directory: {directory_path}")

    return True