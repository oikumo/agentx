import uuid
from pathlib import Path
from uuid import UUID
from pydantic import BaseModel, Field

from agentx.utils.utils_directories import create_directory_if_not_exists, read_file


class ProgramLocation(BaseModel):
    directory: str
    memory_file: str = "main.json"


class ProgramModel:
    location: ProgramLocation | None = None
    memory: ProgramMemory | None = None

    def __init__(self, data: ProgramLocation):
        self.location = data

    def load(self) -> bool:
        if not self.location: return False

        main_path = create_directory_if_not_exists(self.location.directory)
        if not main_path:
            return False

        memory_path = Path(self.location.directory) / self.location.memory_file

        if not Path(memory_path).exists():
            default_memory = ProgramMemory()
            memory_path.write_text(default_memory.model_dump_json(indent=4))

        try:
            file_path = str(memory_path.resolve().absolute())
            self.memory = ProgramMemory.model_validate_json(read_file(file_path))
        except Exception as e:
            print(e)
            return False

        return True

    def save(self) -> bool:
        if not self.memory: return False
        try:
            memory_path = Path(self.location.directory) / self.location.memory_file
            memory_path.write_text(self.memory.model_dump_json(indent=4))
        except Exception as e:
            print(e)
            return False

        return True

    def add_task(self, task: Task) -> bool:
        self.memory.tasks.append(task)
        return self.save()

    def get_task_first(self) -> Task | None:
        return next(iter(self.memory.tasks), None)

class ProgramMemory(BaseModel):
    tasks: list[Task] = []

class Task(BaseModel):
    id: UUID = Field(default_factory=uuid.uuid4)
    name: str = ""
    description: str = ""



