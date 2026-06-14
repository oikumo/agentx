import unittest
from pathlib import Path

from agentx.model.program.program import Program, ProgramLocation
from tests.constants import TEST_SANDBOX_DIR
from tests.testing_utils import dangerous_delete_directory


class TestProgram(unittest.TestCase):
    def test_load(self):
        program_data = ProgramLocation(
            directory=TEST_SANDBOX_DIR + "/test_program",
            memory_file="memory.json"
        )

        test_dir_path = str(Path(program_data.directory).resolve().absolute())
        self.assertTrue(dangerous_delete_directory(test_dir_path))

        program = Program()
        self.assertTrue(program.load(program_data))
        program.add_task("uno", "uno description")
        program.add_task("dos", "dos description")
        task = program.get_task_first()

        self.assertEqual(task.name, "uno")


if __name__ == '__main__':
    unittest.main()
