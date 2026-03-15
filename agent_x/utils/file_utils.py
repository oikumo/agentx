import datetime
import os
from pathlib import Path


def create_directory_with_timestamp(name: str, base_directory) -> str | None:
    now = datetime.datetime.now()
    datetime_string = now.strftime("%Y-%m-%d-%H-%M-%S")
    directory = f"{name}/{datetime_string}"
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