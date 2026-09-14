"""UI Interfaces - rag_v2 contracts (split from ui/interfaces.py; re-exported for compatibility)."""

from __future__ import annotations

from abc import ABC, abstractmethod

class IRagV2View(ABC):
    """Abstract interface for the console RAG v2 outer view."""

    @abstractmethod
    def show(self) -> None:
        """Display the RAG v2 console screen."""
        pass

    @abstractmethod
    def print_message(self, message: str) -> None:
        """Show an info message."""
        pass

    @abstractmethod
    def print_message_error(self, message: str) -> None:
        """Show an error message."""
        pass

    @abstractmethod
    def show_repository_state(self, state: object) -> None:
        """Display repository information."""
        pass

    @abstractmethod
    def show_menu(self) -> None:
        """Display the menu options."""
        pass

    @abstractmethod
    def capture_repository_name(self) -> str:
        """Prompt for a new repository name (console capture)."""
        pass

    @abstractmethod
    def get_selected_repository_id(self) -> str | None:
        """Prompt for a repository id to switch to (console capture)."""
        pass


class IRagV2ViewPartner(ABC):
    """Abstract partner for the RAG v2 view (implemented by RagV2MainController).

    feature_029: ``show_chat`` removed (the `[3] chat` menu entry was a fake
    mode — chat is the REPL's bare-text default); the slash-command
    operations are declared here (ABC honesty).
    """

    @abstractmethod
    def select_repository(self) -> None:
        """Select a repository."""
        pass

    @abstractmethod
    def create_repository(self) -> object:
        """Create a new repository (prompt flow); returns it when created."""
        pass

    @abstractmethod
    def list_repositories(self) -> None:
        """``/repos`` — list on-disk repositories, mark active (feature_029)."""
        pass

    @abstractmethod
    def use_repository(self, repo_id: str | None) -> None:
        """``/use [id]`` — activate a repository; bare falls back to the
        interactive picker (feature_029)."""
        pass

    @abstractmethod
    def create_repository_named(self, name: str | None) -> object:
        """``/create [name]`` — direct create; bare falls back to the prompt
        flow (feature_029)."""
        pass

    @abstractmethod
    def ingest(self, kind: str | None, target: str | None) -> None:
        """``/ingest <web|pdf|md> <target>`` — direct ingestion on the active
        repository (feature_029)."""
        pass

    @abstractmethod
    def show_status(self) -> None:
        """``/status`` — active repo + RAG state + thread id (feature_029)."""
        pass

    @abstractmethod
    def reset_chat(self) -> None:
        """``/reset`` — start a new conversation thread (feature_029)."""
        pass

    @abstractmethod
    def show_web_ingestion(self) -> None:
        """Show the web-ingestion sub-screen."""
        pass

    @abstractmethod
    def show_pdf_ingestion(self) -> None:
        """Show the PDF-ingestion sub-screen (G4)."""
        pass

    @abstractmethod
    def show_md_ingestion(self) -> None:
        """Show the MD-ingestion sub-screen (G4)."""
        pass

    @abstractmethod
    def switch_repository(self) -> None:
        """Switch the active repository (G5)."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the view."""
        pass

    @abstractmethod
    def get_rag_state(self) -> object:
        """Get the RAG repository state."""
        pass


class IRagV2CreateRepositoryView(ABC):
    """Abstract interface for the RAG v2 create-repository sub-screen."""

    @abstractmethod
    def show(self) -> None:
        pass

    @abstractmethod
    def show_error(self, message: str) -> None:
        pass

    @abstractmethod
    def show_success(self, repo_id: str, repo_path: str) -> None:
        pass


class IRagV2CreateRepositoryViewPartner(ABC):
    """Abstract partner for the RAG v2 create-repository view."""

    @abstractmethod
    def on_name_entered(self, name: str) -> bool:
        pass

    @abstractmethod
    def get_prompt(self) -> str:
        pass


class IRagV2RepositorySelectionView(ABC):
    """Abstract interface for the RAG v2 repository-selection sub-screen."""

    @abstractmethod
    def show(self) -> None:
        pass

    @abstractmethod
    def get_selected_index(self) -> int:
        pass


class IRagV2RepositorySelectionViewPartner(ABC):
    """Abstract partner for the RAG v2 repository-selection view."""

    @abstractmethod
    def get_repositories(self) -> "list[str] | None":
        pass


class IRagV2WebIngestionView(ABC):
    """Abstract interface for the RAG v2 web-ingestion sub-screen (G4)."""

    @abstractmethod
    def show(self) -> None:
        pass

    @abstractmethod
    def show_error(self, message: str) -> None:
        pass


class IRagV2WebIngestionViewPartner(ABC):
    """Abstract partner for the RAG v2 web-ingestion view."""

    @abstractmethod
    def ingest_url(self, url: str) -> int:
        pass


class IRagV2PdfIngestionView(ABC):
    """Abstract interface for the RAG v2 PDF-ingestion sub-screen (G4 new)."""

    @abstractmethod
    def show(self) -> None:
        pass

    @abstractmethod
    def show_error(self, message: str) -> None:
        pass


class IRagV2PdfIngestionViewPartner(ABC):
    """Abstract partner for the RAG v2 PDF-ingestion view."""

    @abstractmethod
    def ingest_path(self, pdf_path: str) -> int:
        pass


class IRagV2MdIngestionView(ABC):
    """Abstract interface for the RAG v2 MD-ingestion sub-screen (G4 new)."""

    @abstractmethod
    def show(self) -> None:
        pass

    @abstractmethod
    def show_error(self, message: str) -> None:
        pass


class IRagV2MdIngestionViewPartner(ABC):
    """Abstract partner for the RAG v2 MD-ingestion view."""

    @abstractmethod
    def ingest_path(self, md_path: str) -> int:
        pass
