import unittest

from agent_x.utils.file_utils import create_directory_with_timestamp, directory_exists
from tests.framework_helpers import permanently_delete_test_framework_directories, \
    TEST_SANDBOX_FOLDER


class FileUtilsTest(unittest.TestCase):
    def test_create_directory_with_timestamp(self):
        directory_name = "test_name"
        path = create_directory_with_timestamp(directory_name, TEST_SANDBOX_FOLDER)
        self.assertTrue(directory_name in path)
        self.assertTrue(TEST_SANDBOX_FOLDER in path)
        permanently_delete_test_framework_directories(self, path)

    def test_directory_exits(self):
        directory_name = "test_name_exists"
        base_directory = "utils_test"
        path = create_directory_with_timestamp(directory_name, base_directory)
        self.assertTrue(directory_name in path)
        self.assertTrue(base_directory in path)
        self.assertTrue(directory_exists(path))


