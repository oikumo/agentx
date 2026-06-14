"""
Common file and directory utility functions.

This module provides a comprehensive set of utilities for file and directory
operations using pathlib, following the project's existing conventions.
"""

import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Generator, List, Optional, Union


def create_directory_if_not_exists(path: str) -> Path | None:
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)

    if not is_directory_exists(path):
        return None

    return directory

# ---------------------------------------------------------------------------
# Path coercion
# ---------------------------------------------------------------------------

def _resolve_path(path: Union[str, Path]) -> Path:
    """Coerce a string or Path to an absolute Path."""
    return Path(path).expanduser().resolve()


# ---------------------------------------------------------------------------
# Checks & queries
# ---------------------------------------------------------------------------

def is_file_exists(path: Union[str, Path]) -> bool:
    """Return True if *path* points to an existing file."""
    return Path(path).is_file()


def is_directory_exists(directory: Union[str, Path]) -> bool:
    """Return True if *directory* points to an existing directory."""
    return Path(directory).is_dir()


def is_empty_directory(directory: Union[str, Path]) -> bool:
    """Return True if *directory* exists and contains no entries."""
    p = Path(directory)
    if not p.is_dir():
        return False
    return not any(p.iterdir())


def is_same_path(path1: Union[str, Path], path2: Union[str, Path]) -> bool:
    """Return True if both paths resolve to the same location."""
    return _resolve_path(path1) == _resolve_path(path2)


def get_file_size(path: Union[str, Path]) -> int:
    """Return file size in bytes. Raises FileNotFoundError if missing."""
    return Path(path).stat().st_size


def get_file_extension(path: Union[str, Path]) -> str:
    """Return the file extension including the leading dot (e.g. ``.txt``).

    Returns an empty string when there is no extension.
    """
    return Path(path).suffix


def get_stem(path: Union[str, Path]) -> str:
    """Return the filename without its extension."""
    return Path(path).stem


def get_file_modified_time(path: Union[str, Path]) -> float:
    """Return the last modification timestamp of the file (Unix epoch)."""
    return Path(path).stat().st_mtime


# ---------------------------------------------------------------------------
# Directory creation
# ---------------------------------------------------------------------------

def ensure_directory(path: Union[str, Path], exist_ok: bool = True) -> Path:
    """Create *path* (and any missing parents) if it does not exist.

    Returns the resolved Path.
    """
    p = Path(path)
    p.mkdir(parents=True, exist_ok=exist_ok)
    return p.resolve()


# ---------------------------------------------------------------------------
# Text file I/O
# ---------------------------------------------------------------------------

def read_file(path: Union[str, Path], encoding: str = "utf-8") -> str:
    """Read and return the entire contents of a text file."""
    return Path(path).read_text(encoding=encoding)


def write_file(
    path: Union[str, Path],
    content: str,
    encoding: str = "utf-8",
    ensure_parent: bool = True,
) -> Path:
    """Write *content* to a text file, creating parent directories if needed.

    Returns the resolved Path of the written file.
    """
    p = Path(path)
    if ensure_parent:
        p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding=encoding)
    return p.resolve()


def append_file(
    path: Union[str, Path],
    content: str,
    encoding: str = "utf-8",
    ensure_parent: bool = True,
) -> Path:
    """Append *content* to a text file, creating it (with parents) if missing.

    Returns the resolved Path.
    """
    p = Path(path)
    if ensure_parent:
        p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding=encoding) as f:
        f.write(content)
    return p.resolve()


# ---------------------------------------------------------------------------
# Binary file I/O
# ---------------------------------------------------------------------------

def read_binary_file(path: Union[str, Path]) -> bytes:
    """Read and return the entire contents of a binary file."""
    return Path(path).read_bytes()


def write_binary_file(
    path: Union[str, Path],
    content: bytes,
    ensure_parent: bool = True,
) -> Path:
    """Write *content* to a binary file, creating parent directories if needed.

    Returns the resolved Path.
    """
    p = Path(path)
    if ensure_parent:
        p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(content)
    return p.resolve()


# ---------------------------------------------------------------------------
# JSON I/O
# ---------------------------------------------------------------------------

def read_json(path: Union[str, Path], encoding: str = "utf-8") -> object:
    """Deserialize a JSON file and return the Python object."""
    with Path(path).open("r", encoding=encoding) as f:
        return json.load(f)


def write_json(
    path: Union[str, Path],
    data: object,
    encoding: str = "utf-8",
    indent: int = 2,
    ensure_parent: bool = True,
    **json_kwargs,
) -> Path:
    """Serialize *data* as JSON and write to *path*.

    Returns the resolved Path.
    """
    p = Path(path)
    if ensure_parent:
        p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding=encoding) as f:
        json.dump(data, f, indent=indent, **json_kwargs)
    return p.resolve()


# ---------------------------------------------------------------------------
# File copy / move / delete
# ---------------------------------------------------------------------------

def copy_file(
    src: Union[str, Path],
    dst: Union[str, Path],
    overwrite: bool = False,
) -> Path:
    """Copy *src* to *dst*.

    Raises
    ------
    FileExistsError
        If *dst* exists and *overwrite* is False.
    FileNotFoundError
        If *src* does not exist.
    """
    src_p = _resolve_path(src)
    dst_p = _resolve_path(dst)

    if not src_p.is_file():
        raise FileNotFoundError(f"Source file not found: {src_p}")

    if dst_p.exists() and not overwrite:
        raise FileExistsError(f"Destination already exists: {dst_p}")

    dst_p.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_p, dst_p)
    return dst_p


def move_file(
    src: Union[str, Path],
    dst: Union[str, Path],
    overwrite: bool = False,
) -> Path:
    """Move (rename) *src* to *dst*.

    Raises
    ------
    FileExistsError
        If *dst* exists and *overwrite* is False.
    FileNotFoundError
        If *src* does not exist.
    """
    src_p = _resolve_path(src)
    dst_p = _resolve_path(dst)

    if not src_p.exists():
        raise FileNotFoundError(f"Source not found: {src_p}")

    if dst_p.exists() and not overwrite:
        raise FileExistsError(f"Destination already exists: {dst_p}")

    dst_p.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src_p), str(dst_p))
    return dst_p


def delete_file(path: Union[str, Path], missing_ok: bool = True) -> bool:
    """Delete the file at *path*.

    Returns True if the file was deleted, False if it did not exist
    (when *missing_ok* is True).
    """
    p = Path(path)
    if not p.exists():
        if missing_ok:
            return False
        raise FileNotFoundError(f"File not found: {p}")
    p.unlink()
    return True


# ---------------------------------------------------------------------------
# Listing & searching
# ---------------------------------------------------------------------------

def list_files(
    directory: Union[str, Path],
    pattern: str = "*",
) -> List[Path]:
    """List all files in *directory* matching the glob *pattern*.

    Returns a list of Paths sorted by name.
    """
    p = Path(directory)
    if not p.is_dir():
        return []
    return sorted(p.glob(pattern))


def list_directories(directory: Union[str, Path]) -> List[Path]:
    """List all **immediate** subdirectories of *directory*.

    Returns a list of Paths sorted by name.
    """
    p = Path(directory)
    if not p.is_dir():
        return []
    return sorted([d for d in p.iterdir() if d.is_dir()])


def find_files(
    directory: Union[str, Path],
    pattern: str = "**/*",
) -> Generator[Path, None, None]:
    """Recursively yield files under *directory* matching the glob *pattern*.

    Example patterns::

        find_files("data", "*.json")        # all JSON files
        find_files("src", "**/*.py")        # all Python files
    """
    p = Path(directory)
    if not p.is_dir():
        return
    yield from p.glob(pattern)


# ---------------------------------------------------------------------------
# Directory size
# ---------------------------------------------------------------------------

def get_directory_size(directory: Union[str, Path]) -> int:
    """Walk *directory* and return the total size in bytes."""
    root = Path(directory)
    if not root.is_dir():
        return 0
    total = 0
    for entry in root.rglob("*"):
        if entry.is_file():
            total += entry.stat().st_size
    return total


# ---------------------------------------------------------------------------
# Temporary files / directories
# ---------------------------------------------------------------------------

def create_temp_directory(
    suffix: Optional[str] = None,
    prefix: Optional[str] = None,
) -> Path:
    """Create a temporary directory and return its Path.

    The caller is responsible for cleaning it up.
    """
    return Path(tempfile.mkdtemp(suffix=suffix, prefix=prefix))


def create_temp_file(
    suffix: Optional[str] = None,
    prefix: Optional[str] = None,
    content: str = "",
    encoding: str = "utf-8",
) -> Path:
    """Create a temporary file with optional *content* and return its Path.

    The caller is responsible for cleaning it up.
    """
    fd, path = tempfile.mkstemp(suffix=suffix, prefix=prefix)
    os.close(fd)
    if content:
        Path(path).write_text(content, encoding=encoding)
    return Path(path)


# ---------------------------------------------------------------------------
# Relative path resolution
# ---------------------------------------------------------------------------

def get_relative_path(
    path: Union[str, Path],
    start: Union[str, Path] = ".",
) -> Path:
    """Return *path* relative to *start*.

    Example::

        get_relative_path("/a/b/c/d.txt", "/a/b")  # -> Path("c/d.txt")
    """
    return _resolve_path(path).relative_to(_resolve_path(start))

