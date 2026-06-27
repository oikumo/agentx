"""RAG TUI Screen - Full RAG workflow with repository management and chat.

This screen provides complete RAG functionality:
- Repository listing and selection
- Repository creation
- Document ingestion (web URLs)
- RAG-based chat with documents
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
    DataTable,
    LoadingIndicator,
)
from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
from textual.binding import Binding
from textual.message import Message

from pathlib import Path

if TYPE_CHECKING:
    from agentx.model.rag.rag_repository import RagRepository


class RepositorySelectionScreen(Screen):
    """Screen for selecting a RAG repository."""
    
    BINDINGS = [
        Binding("escape", "cancel", "Cancel", show=True),
        Binding("enter", "select", "Select", show=True),
    ]
    
    DEFAULT_CSS = """
    RepositorySelectionScreen {
        layout: vertical;
    }
    
    RepositorySelectionScreen #repo-table {
        height: 1fr;
        border: solid $primary;
    }
    
    RepositorySelectionScreen #buttons {
        height: auto;
        dock: bottom;
        align: center middle;
    }
    
    RepositorySelectionScreen #buttons Button {
        margin: 0 1;
    }
    """
    
    def __init__(self, rag_working_directory: str) -> None:
        super().__init__()
        self.rag_working_directory = rag_working_directory
        self.selected_repository: RagRepository | None = None
        self.repositories: list[RagRepository] = []
    
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        
        yield Label("Select a RAG Repository:", id="title")
        
        yield DataTable(id="repo-table")
        
        with Horizontal(id="buttons"):
            yield Button("Select", id="btn-select", variant="primary")
            yield Button("Cancel", id="btn-cancel", variant="default")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Load repositories when screen mounts."""
        try:
            from agentx.model.rag.rag_provider import RagProvider
            
            self.notify(f"Loading repositories from: {self.rag_working_directory}", severity="information", timeout=2)
            
            rag_provider = RagProvider(self.rag_working_directory)
            repos = rag_provider.get_repositories()
            
            # Handle None case
            if repos is None:
                self.notify("No repositories found", severity="information", timeout=2)
                repos = []
            else:
                self.notify(f"Found {len(repos)} repositories", severity="information", timeout=2)
            
            # Validate and filter repositories
            self.repositories = []
            for repo in repos:
                if self._validate_repository(repo):
                    self.repositories.append(repo)
                    self.notify(f"✓ Valid: {repo.id}", severity="information", timeout=1)
                else:
                    self.notify(f"✗ Invalid: {repo.id}", severity="warning", timeout=1)
            
            # Populate table
            table = self.query_one("#repo-table", DataTable)
            table.clear()
            table.add_columns("ID", "Path", "Status")
            
            if not self.repositories:
                table.add_row("No repositories", "Found", "N/A")
                self.notify("No valid repositories found. Click 'Create' to make one.", severity="warning", timeout=3)
            else:
                for repo in self.repositories:
                    status = "✓ Valid" if self._validate_repository(repo) else "✗ Invalid"
                    table.add_row(repo.id or "N/A", str(repo.path or "N/A"), status)
                
                self.notify(f"{len(self.repositories)} repository(s) loaded. Select one.", severity="information", timeout=2)
            
            # Enable row selection
            table.cursor_type = "row"
            
        except Exception as e:
            error_msg = f"Error loading repositories: {e}"
            self.notify(error_msg, severity="error", timeout=None)
            # Show error in table
            try:
                table = self.query_one("#repo-table", DataTable)
                table.add_row("Error", str(e), "Failed")
            except Exception:
                pass
    
    def _validate_repository(self, repository) -> bool:
        """Validate repository integrity."""
        import sqlite3
        
        if not repository.id or not repository.path:
            return False
        
        repo_path = Path(repository.path)
        if not repo_path.exists():
            return False
        
        db_path = repo_path / "rag.db"
        if not db_path.exists():
            return False
        
        try:
            conn = sqlite3.connect(str(db_path))
            conn.execute("SELECT 1")
            conn.close()
        except Exception:
            return False
        
        return True
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks."""
        if event.button.id == "btn-select":
            self.action_select()
        elif event.button.id == "btn-cancel":
            self.action_cancel()
    
    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection - alternative to highlighted."""
        table = self.query_one("#repo-table", DataTable)
        cursor_row = table.cursor_row
        
        if cursor_row is not None and isinstance(cursor_row, int):
            if 0 <= cursor_row < len(self.repositories):
                self.selected_repository = self.repositories[cursor_row]
                self.notify(f"Selected: {self.selected_repository.id}", severity="information", timeout=1)
    
    def action_select(self) -> None:
        """Select the highlighted repository."""
        # First try from tracked selection
        if self.selected_repository:
            # Store result in app for callback to retrieve
            self.app.repository_selected = self.selected_repository  # type: ignore[attr-defined]
            self.app.pop_screen()
            return
        
        # Try to get from table cursor
        try:
            table = self.query_one("#repo-table", DataTable)
            cursor_row = table.cursor_row
            if cursor_row is not None and isinstance(cursor_row, int):
                if 0 <= cursor_row < len(self.repositories):
                    self.selected_repository = self.repositories[cursor_row]
                    self.app.repository_selected = self.selected_repository  # type: ignore[attr-defined]
                    self.app.pop_screen()
                    return
        except Exception as e:
            self.notify(f"Error getting selection: {e}", severity="error", timeout=2)
        
        # No selection
        self.notify("No repository selected", severity="warning", timeout=2)
    
    def action_cancel(self) -> None:
        """Cancel selection."""
        self.app.pop_screen()


class RepositoryCreateScreen(Screen):
    """Screen for creating a new RAG repository."""
    
    BINDINGS = [
        Binding("escape", "cancel", "Cancel", show=True),
    ]
    
    DEFAULT_CSS = """
    RepositoryCreateScreen {
        layout: vertical;
    }
    
    RepositoryCreateScreen #name-input {
        width: 50;
        margin: 1 0;
    }
    
    RepositoryCreateScreen #error-message {
        color: red;
        text-style: bold;
    }
    
    RepositoryCreateScreen #success-message {
        color: green;
        text-style: bold;
    }
    """
    
    def __init__(self, rag_working_directory: str) -> None:
        super().__init__()
        self.rag_working_directory = rag_working_directory
        self.created_repository = None
    
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        
        yield Label("Create New RAG Repository", id="title")
        yield Label("Enter repository name (letters, numbers, underscore only):")
        
        yield Input(
            placeholder="my_repository",
            id="name-input",
        )
        
        yield Static("", id="error-message")
        yield Static("", id="success-message")
        
        with Horizontal(id="buttons"):
            yield Button("Create", id="btn-create", variant="primary")
            yield Button("Cancel", id="btn-cancel", variant="default")
        
        yield Footer()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks."""
        if event.button.id == "btn-create":
            self.action_create()
        elif event.button.id == "btn-cancel":
            self.action_cancel()
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in input."""
        if event.input.id == "name-input":
            self.action_create()
    
    def action_create(self) -> None:
        """Create the repository."""
        try:
            input_widget = self.query_one("#name-input", Input)
            name = input_widget.value.strip()
            
            if not name:
                error_widget = self.query_one("#error-message", Static)
                error_widget.update("Repository name cannot be empty")
                return
            
            # Create repository
            from agentx.model.rag.rag_repository import RagRepository
            from agentx.model.rag.rag_db import RagDatabase
            
            import re
            # Validate name
            if len(name) > 50:
                error_widget = self.query_one("#error-message", Static)
                error_widget.update("Repository name too long (max 50 characters)")
                return
            
            if not re.match(r'^[a-zA-Z0-9_]+$', name):
                error_widget = self.query_one("#error-message", Static)
                error_widget.update("Use letters, numbers, underscore only")
                return
            
            if name.startswith('rag_'):
                error_widget = self.query_one("#error-message", Static)
                error_widget.update("Don't include 'rag_' prefix (added automatically)")
                return
            
            # Create directory
            from pathlib import Path
            repo_path = Path(self.rag_working_directory) / f"rag_{name}"
            
            if repo_path.exists():
                error_widget = self.query_one("#error-message", Static)
                error_widget.update(f"Repository '{name}' already exists")
                return
            
            repo_path.mkdir(parents=True, exist_ok=False)
            
            # Initialize database
            db_path = repo_path / "rag.db"
            db = RagDatabase(str(db_path))
            if not db.create_if_not_exists():
                import shutil
                shutil.rmtree(repo_path, ignore_errors=True)
                error_widget = self.query_one("#error-message", Static)
                error_widget.update("Failed to initialize database")
                return
            
            # Success
            self.created_repository = RagRepository(
                id=f"rag_{name}",
                path=str(repo_path)
            )
            
            success_widget = self.query_one("#success-message", Static)
            success_widget.update(f"✓ Repository '{f'rag_{name}'}' created successfully!")
            
            # Close after short delay
            from textual import work
            @work(exclusive=True)
            async def close_after_delay():
                import asyncio
                await asyncio.sleep(1.5)
                # Store result and pop screen
                self.app.created_repository = self.created_repository  # type: ignore[attr-defined]
                self.app.pop_screen()
            
            close_after_delay()
            
        except FileExistsError:
            error_widget = self.query_one("#error-message", Static)
            error_widget.update(f"Repository already exists")
        except Exception as e:
            error_widget = self.query_one("#error-message", Static)
            error_widget.update(f"Error: {e}")
    
    def action_cancel(self) -> None:
        """Cancel creation."""
        self.app.pop_screen()


class WebIngestionScreen(Screen):
    """Screen for ingesting web content into RAG repository."""
    
    BINDINGS = [
        Binding("escape", "cancel", "Cancel", show=True),
    ]
    
    DEFAULT_CSS = """
    WebIngestionScreen {
        layout: vertical;
    }
    
    WebIngestionScreen #url-input {
        width: 80;
        margin: 1 0;
    }
    
    WebIngestionScreen #status {
        height: auto;
        margin: 1 0;
    }
    """
    
    def __init__(self, repository) -> None:
        super().__init__()
        self.repository = repository
        self.ingested = False
    
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        
        yield Label(f"Ingest Web Content into: {self.repository.id}", id="title")
        yield Label("Enter website URL to ingest:")
        
        yield Input(
            placeholder="https://example.com",
            id="url-input",
        )
        
        yield Static("", id="status")
        
        with Horizontal(id="buttons"):
            yield Button("Ingest", id="btn-ingest", variant="primary")
            yield Button("Cancel", id="btn-cancel", variant="default")
        
        yield Footer()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks."""
        if event.button.id == "btn-ingest":
            self.action_ingest()
        elif event.button.id == "btn-cancel":
            self.action_cancel()
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key."""
        if event.input.id == "url-input":
            self.action_ingest()
    
    def action_ingest(self) -> None:
        """Ingest web content."""
        try:
            input_widget = self.query_one("#url-input", Input)
            url = input_widget.value.strip()
            
            if not url:
                status_widget = self.query_one("#status", Static)
                status_widget.update("⚠️  Please enter a URL")
                return
            
            # Perform ingestion
            status_widget = self.query_one("#status", Static)
            status_widget.update("⏳ Ingesting... (this may take a moment)")
            
            from agentx.model.rag.rag import Rag, RagWebExtractLevel
            
            rag = Rag(self.repository.path)
            rag.site_url = url  # type: ignore[assignment]
            
            # Use low extraction level for now
            low_level = RagWebExtractLevel(label="Low", max_depth=1, max_breadth=1, max_pages=100)
            rag.web_ingestion(low_level)
            
            self.ingested = True
            status_widget.update(f"✓ Successfully ingested content from {url}")
            
            # Close after delay
            from textual import work
            @work(exclusive=True)
            async def close_after_delay():
                import asyncio
                await asyncio.sleep(2)
                self.app.pop_screen()
            
            close_after_delay()
            
        except Exception as e:
            status_widget = self.query_one("#status", Static)
            status_widget.update(f"❌ Error: {e}")
    
    def action_cancel(self) -> None:
        """Cancel ingestion."""
        self.app.pop_screen()