from pathlib import Path

from agentx.utils import utils
from agentx.model.rag.rag_repository import RagRepository

RAG_DIR_NAME_REPOSITORY_PREFIX = "rag_"

class RagProvider:
    def __init__(self, rag_working_directory: str):
        self.rag_working_directory = rag_working_directory

    def get_repositories(self) -> list[RagRepository] | None:
        directories = self._get_repositories_locations()
        if not directories: return None
        repositories = [RagRepository(path=str(d.absolute().resolve()), id=d.name)
                        for d in directories if utils.file_exists(d / "rag.db")]

        return repositories

    def _get_repositories_locations(self) -> list[Path] | None:
        if not self.rag_working_directory:
            return None

        return utils.get_directories_start_with(self.rag_working_directory, RAG_DIR_NAME_REPOSITORY_PREFIX)