import unittest
import warnings

from websockets import SecurityError
import shutil
import os
from tests.constants import TEST_SANDBOX_FOLDER

def permanently_delete_test_framework_directories(test_case, directory: str):
    warnings.warn(
        "This function permanently_delete_test_framework_directories() is potentially dangerous and should be used with caution, especially with untrusted input.",
        UserWarning,
        stacklevel=2
    )

    if not test_case or not isinstance(test_case, unittest.TestCase):
        raise SecurityError("Try to delete test folder directories from a non TestCase class")

    if not TEST_SANDBOX_FOLDER in directory:
        raise SecurityError("Try to delete not allowed directories")

    if os.path.isdir(directory):
        try:
            shutil.rmtree(directory)
            print(f"Permanently deleted directory: {directory}")
        except OSError as e:
            print(f"Error deleting {directory}: {e}")
    else:
        print(f"Directory not found or is not a directory: {directory}")
