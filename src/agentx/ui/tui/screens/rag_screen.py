"""RAG TUI Screen - Full RAG workflow with repository management and chat.

This screen provides complete RAG functionality:
- Repository selection
- Repository creation  
- Document ingestion (web URLs)
- RAG-based chat
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import (
    Header,
    Footer,
    Input,
    Label,
    Static,
    Button,
    Rule,
)
from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
from textual.binding import Binding

if TYPE_CHECKING:
    from agentx.model.rag.rag_repository import RagRepository


class RagTUIScreen(Screen):
    """RAG screen with full workflow: select/create repo → ingest → chat.
    
    Features:
    - Repository listing and selection
    - Repository creation
    - Document ingestion (web URLs)
    - RAG-based chat
    - Keyboard shortcuts
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True, priority=True),
        Binding("escape", "back", "Back", show=True),
        Binding("r", "refresh", "Refresh", show=True),
        Binding("i", "ingest", "Ingest", show=True),
        Binding("c", "chat_mode", "Chat", show=True),
    ]

    DEFAULT_CSS = """
    RagTUIScreen {
        background: $surface;
    }
    
    RagTUIScreen #title {
        text-style: bold;
        color: $primary;
        padding: 1 0;
    }
    
    RagTUIScreen #section-repo {
        text-style: bold;
        color: $primary;
    }
    
    RagTUIScreen #section-chat {
        text-style: bold;
        color: $secondary;
    }
    
    RagTUIScreen #repo-name {
        text-style: bold;
        color: $text;
        width: 40;
    }
    
    RagTUIScreen .buttons-line {
        height: auto;
        margin: 1 0;
    }
    
    RagTUIScreen .buttons-line Button {
        margin: 0 1;
        min-width: 10;
    }
    
    RagTUIScreen #chat-status {
        color: $text-muted;
        text-style: italic;
    }
    
    RagTUIScreen #rag-input {
        width: 100%;
    }
    
    RagTUIScreen #rag-input:disabled {
        opacity: 0.5;
    }
    
    RagTUIScreen Rule {
        color: $primary;
    }
    """

    def __init__(self) -> None:
        """Initialize RAG screen."""
        super().__init__()
        self.current_repository = None
        self.chat_history = []
        self.rag_working_directory = self._get_rag_directory()

    def _get_rag_directory(self) -> str:
        """Get RAG working directory from session."""
        try:
            from agentx.model.session.session_manager import SessionManager
            session_controller = SessionManager()
            return session_controller.get_directory_rag()
        except Exception:
            # Default fallback
            from pathlib import Path
            return str(Path.home() / ".agentx" / "rag")

    def compose(self) -> ComposeResult:
        """Compose RAG screen layout - simplified for visibility."""
        yield Header(show_clock=True)
        
        # Title
        yield Label("")
        yield Label("  RAG - Retrieval Augmented Generation", id="title")
        yield Label("")
        
        # Repository section - simple vertical layout
        yield Label("  Repository Management:", id="section-repo")
        yield Label("")
        
        # Repository info line
        repo_horizontal = Horizontal()
        repo_horizontal.add_class("repo-line")
        with repo_horizontal:
            yield Static("  Repository: ", id="repo-label")
            yield Static("None selected", id="repo-name")
        yield repo_horizontal
        
        yield Label("")
        
        # Buttons line
        buttons_horizontal = Horizontal()
        buttons_horizontal.add_class("buttons-line")
        with buttons_horizontal:
            yield Button("Select", id="btn-select", variant="primary")
            yield Button("Create", id="btn-create", variant="default")
            yield Button("Ingest", id="btn-ingest", variant="default")
        yield buttons_horizontal
        
        yield Label("")
        yield Rule()
        yield Label("")
        
        # Chat section
        yield Label("  RAG Chat:", id="section-chat")
        yield Label("")
        yield Static("  Select a repository first to enable RAG chat.", id="chat-status")
        yield Label("")
        yield Input(
            placeholder="  Type your question... (disabled until repository selected)",
            id="rag-input",
            disabled=True,
        )
        
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks."""
        button_id = event.button.id
        
        if button_id == "btn-select":
            self._select_repository()
        elif button_id == "btn-create":
            self._create_repository()
        elif button_id == "btn-ingest":
            self._ingest_documents()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle question submission."""
        if event.input.id != "rag-input":
            return
        
        question = event.value.strip()
        
        if not question:
            return
        
        # Clear input
        event.input.value = ""
        
        # Process question with RAG
        self._ask_question(question)

    def _select_repository(self) -> None:
        """Open repository selection screen."""
        from agentx.ui.tui.screens.rag_screens import RepositorySelectionScreen
        
        # Push the selection screen
        self.app.push_screen(RepositorySelectionScreen(self.rag_working_directory))
    
    def on_mount(self) -> None:
        """Called when screen is mounted."""
        # Show welcome notification
        try:
            self.notify("RAG mode: Select or create a repository to start", severity="information", timeout=3)
        except Exception:
            pass
        
        # Start polling for selection result
        self.set_interval(0.5, self._check_selection_result)
    
    def _check_selection_result(self) -> None:
        """Poll for repository selection result."""
        if hasattr(self.app, 'repository_selected') and self.app.repository_selected:
            repository = self.app.repository_selected
            # Clear the attribute
            delattr(self.app, 'repository_selected')
            # Debug notification
            self.notify(f"DEBUG: Repository received: {repository.id}", severity="information", timeout=2)
            # Handle the selection
            self._on_repository_selected(repository)
    
    def _on_repository_selected(self, repository) -> None:
        """Handle repository selection."""
        self.current_repository = repository
        # Debug notification
        self.notify(f"DEBUG: Updating UI for {repository.id}", severity="information", timeout=2)
        
        # Update UI
        try:
            # Update repository name
            repo_name_widget = self.query_one("#repo-name", Static)
            repo_name_widget.update(repository.id or "Unknown")
            self.notify(f"DEBUG: Updated repo name widget", severity="information", timeout=1)
            
            # Enable chat input
            input_widget = self.query_one("#rag-input", Input)
            input_widget.disabled = False
            input_widget.placeholder = "Type your question about the documents..."
            self.notify(f"DEBUG: Enabled chat input", severity="information", timeout=1)
            
            # Update status
            status_widget = self.query_one("#chat-status", Static)
            status_widget.update(f"✓ Ready to chat with: {repository.id}")
            self.notify(f"DEBUG: Updated status", severity="information", timeout=1)
            
            self.notify(f"✓ Selected repository: {repository.id}", severity="information", timeout=2)
        except Exception as e:
            self.notify(f"❌ Error updating UI: {e}", severity="error", timeout=None)
            import traceback
            self.notify(traceback.format_exc()[:200], severity="error", timeout=5)
    
    def _create_repository(self) -> None:
        """Open repository creation screen."""
        from agentx.ui.tui.screens.rag_screens import RepositoryCreateScreen
        
        def on_created(repository):
            """Handle repository creation."""
            if repository:
                self.notify(f"Created repository: {repository.id}", severity="information", timeout=2)
                # Auto-select the created repository
                self.current_repository = repository
                self._update_repository_ui()
        
        self.app.push_screen(
            RepositoryCreateScreen(self.rag_working_directory),
            callback=on_created
        )

    def _ingest_documents(self) -> None:
        """Open web ingestion screen."""
        if not self.current_repository:
            self.notify("Please select a repository first", severity="warning", timeout=2)
            return
        
        from agentx.ui.tui.screens.rag_screens import WebIngestionScreen
        
        def on_ingested(success):
            """Handle ingestion completion."""
            if success:
                self.notify("Documents ingested successfully!", severity="information", timeout=2)
            else:
                self.notify("Ingestion cancelled", severity="information", timeout=2)
        
        self.app.push_screen(
            WebIngestionScreen(self.current_repository),
            callback=on_ingested
        )

    def _update_repository_ui(self) -> None:
        """Update UI to reflect selected repository."""
        try:
            if self.current_repository:
                repo_name_widget = self.query_one("#repo-name", Static)
                repo_name_widget.update(self.current_repository.id or "Unknown")
                
                # Enable chat input
                input_widget = self.query_one("#rag-input", Input)
                input_widget.disabled = False
                input_widget.placeholder = "Type your question about the documents..."
                
                # Update status
                status_widget = self.query_one("#chat-status", Static)
                status_widget.update(f"✓ Ready to chat with: {self.current_repository.id}")
        except Exception:
            pass

    def _ask_question(self, question: str) -> None:
        """Ask a question using RAG."""
        if not self.current_repository:
            self.notify("Please select a repository first", severity="warning", timeout=2)
            return
        
        try:
            # Query RAG
            from agentx.model.rag.rag import Rag
            
            rag = Rag(self.current_repository.path)
            
            # Get answer (simple query for now)
            # TODO: Implement proper RAG retrieval with context
            answer = rag.query(question)
            
            # Display answer
            status_widget = self.query_one("#chat-status", Static)
            status_widget.update(f"Q: {question}\nA: {answer}")
            
            self.notify("Answer retrieved", severity="information", timeout=2)
            
        except Exception as e:
            try:
                self.notify(f"Error: {str(e)}", severity="error", timeout=None)
            except Exception:
                pass

    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()

    def action_back(self) -> None:
        """Go back to main screen."""
        self.app.pop_screen()

    def action_refresh(self) -> None:
        """Refresh repository list."""
        try:
            self.notify("Refreshing repositories...", severity="information", timeout=1)
            # If repository is selected, re-validate it
            if self.current_repository:
                self._update_repository_ui()
        except Exception:
            pass

    def action_ingest(self) -> None:
        """Open ingestion screen."""
        self._ingest_documents()

    def action_chat_mode(self) -> None:
        """Focus chat input."""
        if self.current_repository:
            try:
                input_widget = self.query_one("#rag-input", Input)
                input_widget.focus()
            except Exception:
                pass
        else:
            self.notify("Select a repository first to enable chat", severity="warning", timeout=2)