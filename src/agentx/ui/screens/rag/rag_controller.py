from __future__ import annotations

from dataclasses import dataclass

from agentx.ui.screens.rag.rag_chat_controller import RagChatController
from agentx.ui.screens.rag.rag_repository_selection_controller import RagRepositorySelectionController
from agentx.ui.screens.rag.rag_web_ingestion_controller import RagWebIngestionController
from agentx.model.session.session_manager import SessionManager
from agentx.model.rag.rag_repository import RagRepository
from agentx.ui.screens.rag.rag_view import RagView
from agentx.ui.interfaces import IRagView

@dataclass
class RagState:
    url: str | None
    data_base_location: str | None
    documents_location: str | None

class RagController:
    view: IRagView
    current_rag_repository: RagRepository | None

    def __init__(self, view: IRagView | None = None) -> None:
        self.view = view if view else RagView(self)
        self.session_controller = SessionManager()
        self.rag_working_directory = self.session_controller.get_directory_rag()
        self.current_rag_repository = None

    def show(self):
        if self.view: self.view.show()

    def select_repository(self):
        repository_selection = RagRepositorySelectionController(self.rag_working_directory)
        repository_selection.show()
        self.current_rag_repository = repository_selection.get_selected_repository()
        
        if self.current_rag_repository:
            self.view.print_message(f"Selected repository: {self.current_rag_repository.id}")
        else:
            self.view.print_message("No repository selected.")
    
    def create_repository(self) -> None:
        """Create new repository."""
        from agentx.ui.screens.rag.rag_create_repository_controller import RagCreateRepositoryController
        
        creator = RagCreateRepositoryController(self.rag_working_directory)
        new_repo = creator.show()
        
        if new_repo:
            self.view.print_message(f"Repository '{new_repo.id}' created successfully!")
            self.view.print_message("Please select it from the repository list to use.")

    def show_chat(self):
        if not self.current_rag_repository: return
        chat = RagChatController(self.current_rag_repository)
        chat.show()

    def show_web_ingestion(self):
        if not self.current_rag_repository: return
        ingestion = RagWebIngestionController(self.current_rag_repository)
        ingestion.show()

    def close(self) -> None:
        if self.view: self.view.print_message("close")

    def get_rag_state(self) -> RagState | None:
        """
        Get current repository state.
        Returns RagState with repository information or None if no repository selected.
        """
        if not self.current_rag_repository:
            return None
        
        # Check repository has a path
        if not self.current_rag_repository.path:
            return None
        
        try:
            # Import Rag class
            from agentx.model.rag.rag import Rag
            
            # Create Rag instance for this repository
            rag = Rag(working_directory=self.current_rag_repository.path)
            
            # Initialize state variables
            data_base_path: str | None = None
            documents_path: str | None = None
            url: str | None = None
            
            # Check database
            if rag.database_exists():
                data_base_path = rag.vector_db_path
                url = rag.get_ingested_url()
            
            # Check documents
            if rag.documents_exist():
                documents_path = rag.documents_path
            
            return RagState(
                url=url,
                data_base_location=data_base_path,
                documents_location=documents_path
            )
            
        except Exception as e:
            print(f"Error retrieving repository state: {e}")
            return None

