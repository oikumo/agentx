import datetime
import os.path
from pathlib import Path


class Session:
    def __init__(self, name: str):
        if not (name and name.strip):
            raise Exception()

        self.name = name
        self.directory = ""

    def create(self):
        now = datetime.datetime.now()
        datetime_string = now.strftime("%Y-%m-%d-%H-%M-%S")
        directory = f"{self.name}/{datetime_string}"
        session_directory = f"sessions/web_ingestion/{directory}"

        if os.path.isdir(session_directory):
            raise FileExistsError()

        directory_path = Path(session_directory)
        directory_path.mkdir(parents=True, exist_ok=True)

        if not os.path.isdir(session_directory):
            raise Exception("create directory error")

        self.directory = directory_path.absolute()
