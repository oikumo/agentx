from agentx.common.security import SESSION_DEFAULT_NAME, SESSION_DEFAULT_BASE_DIRECTORY
from agentx.common.utils import create_directory_with_timestamp, create_directory_without_timestamp, directory_exists, dangerous_delete_directory



class Session:
    __directory: str | None
    __session_name: str
    __use_timestamp: bool

    @property
    def name(self) -> str:
        return self.__session_name

    @property
    def directory(self) -> str | None:
        return self.__directory

    def __init__(self, name: str, use_timestamp: bool = True):
        self.__directory = None
        self.__session_name = SESSION_DEFAULT_NAME
        self.__use_timestamp = use_timestamp
        if not (name and name.strip()):
            self.__session_name = SESSION_DEFAULT_NAME
        elif " " in name:
            self.__session_name = name.replace(" ", "_").lower()
        else:
            self.__session_name = name

    def create(self):
        self.__directory = None
        if self.__use_timestamp:
            new_directory = create_directory_with_timestamp(
                self.__session_name, SESSION_DEFAULT_BASE_DIRECTORY
            )
        else:
            new_directory = create_directory_without_timestamp(
                self.__session_name, SESSION_DEFAULT_BASE_DIRECTORY
            )
        if not new_directory:
            return False
        self.__directory = new_directory
        return True

    def is_created(self):
        if not self.__directory:
            return False
        return directory_exists(self.__directory)
