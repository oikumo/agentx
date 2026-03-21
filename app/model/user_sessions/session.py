from app.security.security_constants import SESSION_DEFAULT_NAME, SESSION_DEFAULT_BASE_DIRECTORY
from app.common.utils.file_utils import create_directory_with_timestamp, directory_exists, dangerous_delete_directory


class Session:
    __directory: str | None = None
    __session_name: str = SESSION_DEFAULT_NAME

    @property
    def name(self):
        return self.__session_name

    @property
    def directory(self):
        return self.__directory

    def __init__(self, name: str):
        if not (name and name.strip()):
            self.__session_name = SESSION_DEFAULT_NAME
        elif " " in name:
            self.__session_name = name.replace(" ", "_").lower()
        else:
            self.__session_name = name

    def create(self):
        self.__directory = None
        new_directory = create_directory_with_timestamp(self.__session_name, SESSION_DEFAULT_BASE_DIRECTORY)
        if not new_directory:
            return False
        self.__directory = new_directory

        return True

    def is_created(self):
        if not self.__directory:
            return False
        return directory_exists(self.__directory)

    def destroy(self) -> bool:
        if not self.is_created():
            return False

        dangerous_delete_directory(self.__directory)

        return True



