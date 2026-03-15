from typing import Final, List


SESSION_DEFAULT_NAME: Final[str] = "default"
SESSION_DEFAULT_BASE_DIRECTORY: Final[str] = "local_sessions"

DIRECTORIES_DELETION_ALLOWED: Final[List[str]] = [SESSION_DEFAULT_BASE_DIRECTORY]

def is_directory_allowed_to_deletion(directory_path: str) -> bool:
    if not directory_path in DIRECTORIES_DELETION_ALLOWED:
        raise PermissionError(f"trying to delete a directory not allowed for deletion. Directory: {directory_path}")
    return True