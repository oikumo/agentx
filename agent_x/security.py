from pathlib import Path
from typing import Final, List

SESSION_DEFAULT_NAME: Final[str] = "default"
SESSION_DEFAULT_BASE_DIRECTORY: Final[str] = "local_sessions"

DIRECTORIES_DELETION_ALLOWED: Final[List[str]] = [SESSION_DEFAULT_BASE_DIRECTORY]

def is_directory_allowed_to_deletion(directory_path: str) -> bool:
    if not DIRECTORIES_DELETION_ALLOWED:
        raise PermissionError(f"trying to delete a directory but filter is empty, Directory: {directory_path}")

    current_directory: Final[Path] = Path.cwd()
    candidate_directory_path: Final[Path] = Path(directory_path)

    if not candidate_directory_path.is_relative_to(current_directory):
        raise PermissionError(f"trying to delete a directory when is out of current directory. Directory: {directory_path}")

    allowed_directories: List[Path] = []

    for directory_allowed in DIRECTORIES_DELETION_ALLOWED:
        allowed_directory = current_directory / directory_allowed
        allowed_directories.append(allowed_directory)

    for allowed_directory in allowed_directories:
        if candidate_directory_path.relative_to(allowed_directory):
            return True

    raise PermissionError(f"trying to delete a directory not allowed for deletion. Directory: {directory_path}")
