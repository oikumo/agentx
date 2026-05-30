from agentx.app.rag_controller.rag_create_repository_controller import RagCreateRepositoryController
from agentx.model.rag.rag_provider import RagRepository, RagProvider
from agentx.app.rag_controller.rag_repostitory_selection_view import RagRepositorySelectionView


class RagRepositorySelectionController:
    def __init__(self, rag_working_directory: str):
        self.view = RagRepositorySelectionView(self)
        self.rag_provider = RagProvider(rag_working_directory)

    def show(self) -> None:
        self.view.show()

    def get_repositories(self) -> list[str] | None:
        if not self.rag_provider.get_repositories(): return None
        return [r.id for r in self.rag_provider.get_repositories()]

    def createRepository(self) -> None:
        new_repository = RagCreateRepositoryController()
        new_repository.show()


    def get_selected_repository(self) -> RagRepository | None:
        return None

    def close(self):
        pass