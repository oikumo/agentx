from agentx.model.program.program_model import ProgramModel, ProgramLocation, Task


class Program:
    persistence: ProgramModel = ProgramModel | None

    def __init__(self):
        pass

    def load(self, program_data: ProgramLocation) -> bool:
        self.persistence = ProgramModel(program_data)
        if not self.persistence.load(): return False
        return True

    def add_task(self, name: str, description: str) -> bool:
        task = Task(
            name=name,
            description= description
        )

        return self.persistence.add_task(task)

    def get_task_first(self) -> Task | None:
        return self.persistence.get_task_first()