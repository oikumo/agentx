from typing import Final

from agent_x.utils.file_utils import create_directory_with_timestamp, directory_exists

SESSION_DEFAULT_NAME: Final[str] = "DEFAULT"
SESSION_DEFAULT_BASE_DIRECTORY: Final[str] = "sessions"


class Session:
    def __init__(self, name: str, base_directory: str = SESSION_DEFAULT_BASE_DIRECTORY):
        if not (name and name.strip()):
            self.name = SESSION_DEFAULT_NAME
        elif " " in name:
            self.name = name.replace(" ", "_")
        else:
            self.name = name
        self.base_directory = base_directory
        self.directory: str | None = None

    def create(self):
        self.directory = None
        new_directory = create_directory_with_timestamp(self.name, self.base_directory)
        if not new_directory:
            return False
        self.directory = new_directory

        return True

    def is_created(self):
        if not self.directory:
            return False
        return directory_exists(self.directory)


