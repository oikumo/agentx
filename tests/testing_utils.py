import os
import shutil
from pathlib import Path

from tests.constants import TEST_DIRECTORIES_DELETION_ALLOWED


def is_directory_allowed_to_deletion(directory_path: str) -> bool:
    if not TEST_DIRECTORIES_DELETION_ALLOWED:
        raise PermissionError(
            f"trying to delete a directory but filter is empty, Directory: {directory_path}"
        )

    current_directory: Path = Path.cwd()
    candidate_directory_path: Path = Path(directory_path)

    try:
        candidate_directory_path.is_relative_to(current_directory)
    except Exception as e:
        print(e)
        raise PermissionError(
            f"trying to delete a directory when is out of current directory. Directory: {directory_path}"
        )

    allowed_directories = []
    for directory_allowed in TEST_DIRECTORIES_DELETION_ALLOWED:
        allowed_directory = current_directory / directory_allowed
        allowed_directories.append(allowed_directory)

    for allowed_directory in allowed_directories:
        try:
            candidate_directory_path.relative_to(allowed_directory)
            return True
        except Exception as e:
            print(e)

    raise PermissionError(
        f"trying to delete a directory not allowed for deletion. Directory: {directory_path}"
    )


def dangerous_delete_directory(directory_path: str) -> bool:
    if not is_directory_allowed_to_deletion(directory_path):
        return False

    if not os.path.isdir(directory_path):
        print(f"Directory not found or is not a directory: {directory_path}")
        return True

    shutil.rmtree(directory_path)
    print(f"Permanently deleted directory: {directory_path}")

    return True
