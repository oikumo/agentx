import unittest

from agent_x.utils.file_utils import create_directory_with_timestamp, directory_exists


class FileUtilsTest(unittest.TestCase):
    def test_create_directory_with_timestamp(self):
        directory_name = "test_name"
        base_directory = "utils_test"
        path = create_directory_with_timestamp(directory_name, base_directory)
        self.assertTrue(directory_name in path)
        self.assertTrue(base_directory in path)

    def test_directory_exits(self):
        directory_name = "test_name_exists"
        base_directory = "utils_test"
        path = create_directory_with_timestamp(directory_name, base_directory)
        self.assertTrue(directory_name in path)
        self.assertTrue(base_directory in path)
        self.assertTrue(directory_exists(path))


