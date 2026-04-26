import os
import time
import datetime
import shutil
import warnings
from pathlib import Path


def safe_int(value: str) -> int | None:
    try:
        return int(value)
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


def directory_exists(directory: str):
    return os.path.isdir(directory)


def save_to_output(text: str):
    with open("local/output.txt", "w") as file:
        file.write(text)


def is_directory_allowed_to_deletion(directory_path: str) -> bool:
    from agentx.common.security import DIRECTORIES_DELETION_ALLOWED

    if not DIRECTORIES_DELETION_ALLOWED:
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
    for directory_allowed in DIRECTORIES_DELETION_ALLOWED:
        allowed_directory = current_directory / directory_allowed
        allowed_directories.append(allowed_directory)

    for allowed_directory in allowed_directories:
        try:
            candidate_directory_path.relative_to(allowed_directory)
            return True
        except Exception:
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

    if not os.path.isdir(directory_path):
        print(f"Directory not found or is not a directory: {directory_path}")
        return False

    shutil.rmtree(directory_path)
    print(f"Permanently deleted directory: {directory_path}")

    return True


class StreamingMetrics:
    def __init__(self):
        self._start_time: float | None = None
        self._elapsed_time: float = 0.0
        self._total_tokens: int = 0
        self._is_started: bool = False

    @property
    def total_tokens(self) -> int:
        return self._total_tokens

    @property
    def elapsed_time(self) -> float:
        return self._elapsed_time

    @property
    def is_started(self) -> bool:
        return self._is_started

    @property
    def tokens_per_second(self) -> float:
        if self._elapsed_time == 0 or self._total_tokens == 0:
            return 0.0
        return self._total_tokens / self._elapsed_time

    def start(self) -> None:
        self._start_time = time.perf_counter()
        self._is_started = True

    def stop(self) -> None:
        if self._start_time is None:
            raise RuntimeError("Cannot stop metrics that were never started")
        self._elapsed_time = time.perf_counter() - self._start_time
        self._is_started = False

    def add_tokens(self, count: int) -> None:
        self._total_tokens += count

    def add_text(self, text: str) -> None:
        self._total_tokens += len(text)

    def format(self) -> str:
        return f"{self._total_tokens} tokens in {self._elapsed_time:.1f}s ({self.tokens_per_second:.1f} tok/s)"

    def __enter__(self) -> "StreamingMetrics":
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.stop()
