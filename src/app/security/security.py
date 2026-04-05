from pathlib import Path
from typing import Final, List

from app.security.security_constants import DIRECTORIES_DELETION_ALLOWED


def is_directory_allowed_to_deletion(directory_path: str) -> bool:
    if not DIRECTORIES_DELETION_ALLOWED:
        raise PermissionError(f"trying to delete a directory but filter is empty, Directory: {directory_path}")

    current_directory: Final[Path] = Path.cwd()
    candidate_directory_path: Final[Path] = Path(directory_path)

    try:
        candidate_directory_path.is_relative_to(current_directory)
    except Exception as e:
        print(e)
        raise PermissionError(f"trying to delete a directory when is out of current directory. Directory: {directory_path}")

    allowed_directories: List[Path] = []

    for directory_allowed in DIRECTORIES_DELETION_ALLOWED:
        allowed_directory = current_directory / directory_allowed
        allowed_directories.append(allowed_directory)

    for allowed_directory in allowed_directories:
        try:
            candidate_directory_path.relative_to(allowed_directory)
            return True
        except Exception:
            pass

    raise PermissionError(f"trying to delete a directory not allowed for deletion. Directory: {directory_path}")
