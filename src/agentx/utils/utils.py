import os
import time
import datetime
import shutil
import warnings
from pathlib import Path

from agentx.utils import utils_directories
from agentx.utils.utils_directories import is_directory_exists


def safe_int(value: object) -> int | None:
    # Reject bool explicitly (bool subclasses int — int(True)==1 hides bugs
    # in menu/coordinate parsing). Accept int directly, numeric strings
    # (whitespace-tolerant); everything else (float, None, junk) → None.
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if not isinstance(value, str):
        return None
    text = value.strip()
    if not text:
        return None
    try:
        return int(text)
    except (ValueError, TypeError):
        return None


def clear_console():
    if os.name == "nt":
        _ = os.system("cls")
    else:
        _ = os.system("clear")


def create_directory_with_timestamp(name: str, base_directory) -> str | None:
    now = datetime.datetime.now()
    datetime_string = now.strftime("%Y-%m-%d-%H-%M-%S")
    directory = f"{name}_{datetime_string}"
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


def create_directory_without_timestamp(name: str, base_directory) -> str | None:
    """Create a directory without timestamp (for current session)."""
    directory = f"{name}"
    session_directory = f"{base_directory}/{directory}"
    
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

def get_directories_start_with(base_directory: str, prefix: str) -> list[Path]:
    if not is_directory_exists(base_directory):
        return []

    base_path = Path(base_directory)
    directories = [d for d in base_path.iterdir() if d.is_dir() and d.name.startswith(prefix)]

    return directories


def save_to_output(text: str):
    with open("local/output.txt", "w") as file:
        file.write(text)


def is_directory_allowed_to_deletion(directory_path: str) -> bool:
    """AXR-12: canonical containment guard (shared path policy with AXR-01/02).

    Resolve + normalize the candidate and every trusted allowed root, then
    require explicit containment. Lexical prefix checks without resolve()
    accept `<allow>/../outside` and outside symlink targets. The validated
    canonical path is what callers must delete (see dangerous_delete_directory).
    Contract preserved: disallowed -> PermissionError (not False).
    Policy: deleting an allowed root itself is permitted (relative_to allows
    equality); allowed roots are resolved as configured (caller trust).
    Residual: resolve-then-check does not cover concurrent rename races;
    bound = stable directory ancestry (same bound as AXR-01/02).
    """
    from agentx.utils.constants import DIRECTORIES_DELETION_ALLOWED

    if not DIRECTORIES_DELETION_ALLOWED:
        raise PermissionError(
            f"trying to delete a directory but filter is empty, Directory: {directory_path}"
        )

    current_directory: Path = Path.cwd().resolve()
    raw = Path(directory_path)
    if not raw.is_absolute():
        raw = current_directory / raw
    try:
        candidate = raw.resolve()
    except Exception:
        raise PermissionError(
            f"trying to delete a directory when is out of current directory. Directory: {directory_path}"
        )

    try:
        candidate.relative_to(current_directory)
    except ValueError:
        raise PermissionError(
            f"trying to delete a directory when is out of current directory. Directory: {directory_path}"
        )

    allowed_directories = []
    for directory_allowed in DIRECTORIES_DELETION_ALLOWED:
        allowed_raw = Path(directory_allowed)
        if not allowed_raw.is_absolute():
            allowed_raw = current_directory / allowed_raw
        try:
            allowed_directories.append(allowed_raw.resolve())
        except Exception:
            continue

    for allowed_directory in allowed_directories:
        try:
            candidate.relative_to(allowed_directory)
            return True
        except ValueError:
            pass

    raise PermissionError(
        f"trying to delete a directory not allowed for deletion. Directory: {directory_path}"
    )


def dangerous_delete_directory(directory_path: str) -> bool:
    warnings.warn(
        "This function dangerous_delete_directory() is potentially dangerous and should be used with caution, especially with untrusted input.",
        UserWarning,
        stacklevel=2,
    )

    if not is_directory_allowed_to_deletion(directory_path):
        return False

    # Delete the validated canonical path, not the lexical caller input, so
    # `<allow>/../outside` or a symlink form cannot address another target
    # between guard and removal (same stable-ancestry bound as guard).
    current_directory: Path = Path.cwd().resolve()
    raw = Path(directory_path)
    if not raw.is_absolute():
        raw = current_directory / raw
    try:
        canonical = str(raw.resolve())
    except Exception:
        return False

    if not os.path.isdir(canonical):
        print(f"Directory not found or is not a directory: {directory_path}")
        return False

    shutil.rmtree(canonical)
    print(f"Permanently deleted directory: {directory_path}")

    return True
# TA: AXR-12 guard: resolve+normalize candidate and allowed roots, explicit relative_to containment, PermissionError contract kept; deletion uses validated canonical path; concurrent-rename bound = stable ancestry (pkg1 agentx_1_0_0).
