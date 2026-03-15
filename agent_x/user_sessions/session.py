from agent_x.constants import SESSION_DEFAULT_NAME, SESSION_DEFAULT_BASE_DIRECTORY
from agent_x.utils.file_utils import create_directory_with_timestamp, directory_exists

class Session:
    def __init__(self, name: str, sessions_directory: str = SESSION_DEFAULT_BASE_DIRECTORY):
        if not (name and name.strip()):
            self.name = SESSION_DEFAULT_NAME
        elif " " in name:
            self.name = name.replace(" ", "_")
        else:
            self.name = name
        self.directory: str | None = None
        self.sessions_directory = sessions_directory

    def create(self):
        self.directory = None
        new_directory = create_directory_with_timestamp(self.name, self.sessions_directory)
        if not new_directory:
            return False
        self.directory = new_directory

        return True

    def is_created(self):
        if not self.directory:
            return False
        return directory_exists(self.directory)

    def destroy(self):
        pass



