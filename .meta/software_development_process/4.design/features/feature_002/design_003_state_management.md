# DESIGN: RAG State Management

## Overview
This document details the design for implementing repository state retrieval and display functionality.

---

## Architecture

### Component Diagram
```
┌─────────────────────────────────────────────────────────────┐
│                    RAG Main Menu                             │
│                      (RagController)                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  get_rag_state()                                      │   │
│  │    ↓                                                  │   │
│  │  Check current_rag_repository                         │   │
│  │    ↓                                                  │   │
│  │  Create Rag instance                                  │   │
│  │    ↓                                                  │   │
│  │  Query state (URL, DB path, docs path)                │   │
│  │    ↓                                                  │   │
│  │  Return RagState                                      │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ returns RagState
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    RagView                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  display_state(RagState)                              │   │
│  │    - Show repository name                             │   │
│  │    - Show repository path                             │   │
│  │    - Show database location                           │   │
│  │    - Show documents location                          │   │
│  │    - Show ingested URL (if available)                 │   │
│  │    - Show status (empty/data available)               │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Class Design

### 1. RagController (EXTEND)

**Location:** `src/agentx/ui/screens/rag/rag_controller.py`

**Current State:** `get_rag_state()` returns `None` with commented implementation

**New Implementation:**
```python
class RagController:
    view: RagView
    current_rag_repository: RagRepository | None
    
    def __init__(self) -> None:
        self.view = RagView(self)
        self.session_controller = SessionController()
        self.rag_working_directory = self.session_controller.get_directory_rag()
        self.current_rag_repository = None
    
    def get_rag_state(self) -> RagState | None:  # FIX THIS
        """
        Get current repository state.
        Returns RagState with repository information or None if no repository selected.
        """
        if not self.current_rag_repository:
            return None
        
        try:
            # Create Rag instance for selected repository
            from agentx.model.rag.rag import Rag
            rag = Rag(working_directory=self.current_rag_repository.path)
            
            # Check what data exists
            data_base_path = None
            documents_path = None
            url = None
            
            # Check database exists
            if rag.database_exists():
                data_base_path = rag.vector_db_path
                # Try to get URL from database
                url = rag.get_ingested_url()
            
            # Check documents exist
            if rag.documents_exist():
                documents_path = rag.documents_path
            
            return RagState(
                url=url,
                data_base_location=data_base_path,
                documents_location=documents_path
            )
            
        except Exception as e:
            # Log error but don't crash
            print(f"Error retrieving repository state: {e}")
            return None
    
    def _format_repository_state(self, state: RagState) -> str:
        """
        Format repository state for display.
        Returns formatted string.
        """
        if not state:
            return "No repository selected"
        
        lines = []
        lines.append(f"Repository: {self.current_rag_repository.id}")
        lines.append(f"Path: {self.current_rag_repository.path}")
        lines.append("─" * 50)
        
        if state.data_base_location:
            lines.append(f"Database: {state.data_base_location}")
        else:
            lines.append("Database: Not initialized")
        
        if state.documents_location:
            lines.append(f"Documents: {state.documents_location}")
        else:
            lines.append("Documents: No documents ingested")
        
        if state.url:
            lines.append(f"Ingested URL: {state.url}")
        
        return "\n".join(lines)
```

---

### 2. Rag (EXTEND - MAYBE)

**Location:** `src/agentx/model/rag/rag.py`

**Verify/Add Methods:**

```python
class Rag:
    def __init__(self, working_directory: str):
        self.working_directory = working_directory
        self.vector_db_path = os.path.join(working_directory, "chroma_db")
        self.documents_path = os.path.join(working_directory, "documents.jsonl")
        self.database_path = os.path.join(working_directory, "rag.db")
        self.site_url: str | None = None
        # ... rest of init
    
    def database_exists(self) -> bool:  # ADD IF MISSING
        """Check if SQLite database exists."""
        return os.path.exists(self.database_path)
    
    def documents_exist(self) -> bool:  # ADD IF MISSING
        """Check if documents file exists."""
        return os.path.exists(self.documents_path)
    
    def get_ingested_url(self) -> str | None:  # ADD IF MISSING
        """Get URL from ingestion history."""
        if not self.database_exists():
            return None
        
        try:
            from agentx.model.rag.rag_db import RagDatabase
            db = RagDatabase(self.database_path)
            ingestions = db.get_all_ingestions()
            
            if ingestions:
                # Return most recent URL
                return ingestions[-1].url
            return None
        except Exception:
            return None
```

**Note:** May need to verify these methods exist or add them

---

### 3. RagView (EXTEND)

**Location:** `src/agentx/ui/screens/rag/rag_view.py`

**Required Changes:**
```python
class RagView:
    def __init__(self, controller: RagController):
        self._controller = controller
        self._console = UIConsole("(rag)")
    
    def show(self) -> None:
        """Display main menu with repository state."""
        while True:
            # Get and display state
            state = self._controller.get_rag_state()
            self._display_repository_state(state)
            
            # Display menu
            self._console.print("")
            self._console.print("Options:")
            self._console.print("[1] Select Repository")
            self._console.print("[2] Create Repository")
            self._console.print("[3] Web Ingestion")
            self._console.print("[4] RAG Chat")
            self._console.print("[5] Quit")
            self._console.print("")
            
            # Capture input
            selection = self._console.capture_input("Select option: ").strip()
            
            # Handle selection
            if selection == "1":
                self._controller.select_repository()
            elif selection == "2":
                self._controller.create_repository()
            elif selection == "3":
                self._controller.show_web_ingestion()
            elif selection == "4":
                self._controller.show_chat()
            elif selection in ["5", "q", "quit", "exit"]:
                self._controller.close()
                return
            else:
                self._console.print("Invalid option. Please try again.")
    
    def _display_repository_state(self, state: RagState | None) -> None:
        """Display repository state header."""
        self._console.print("")
        self._console.print("═" * 50)
        
        if not state:
            self._console.print("⚠️  No repository selected")
            self._console.print("   Please select or create a repository to continue")
        else:
            self._console.print(f"📁 Repository: {self._controller.current_rag_repository.id}")
            self._console.print(f"   Path: {state.data_base_location or 'N/A'}")
            
            if state.url:
                self._console.print(f"   Ingested: {state.url}")
            else:
                self._console.print("   Status: Empty (no data ingested)")
        
        self._console.print("═" * 50)
        self._console.print("")
```

---

## Sequence Diagrams

### State Retrieval Success
```
RagView        RagController      RagRepository      Rag              RagDatabase
 │                │                    │               │                  │
 │ show()         │                    │               │                  │
 ├───────────────►│                    │               │                  │
 │                │                    │               │                  │
 │ get_rag_state()│                    │               │                  │
 ├───────────────►│                    │               │                  │
 │                │                    │               │                  │
 │                │ check repository   │               │                  │
 │                │ (exists)           │               │                  │
 │                │                    │               │                  │
 │                │ create Rag(repo)   │               │                  │
 │                ├──────────────────────────────────►│                  │
 │                │                    │               │                  │
 │                │                    │               │ database_exists()│
 │                │                    │               ├─────────────────►│
 │                │                    │               │                  │
 │                │                    │               │◄─────────────────│
 │                │                    │               │                  │
 │                │                    │               │ get_ingested_url()
 │                │                    │               ├─────────────────►│
 │                │                    │               │                  │
 │                │                    │               │◄─────────────────│
 │                │                    │               │                  │
 │                │◄───────────────────────────────────│                  │
 │                │ RagState                           │                  │
 │◄───────────────│                    │               │                  │
 │ display state  │                    │               │                  │
 │◄───────────────│                    │               │                  │
```

### No Repository Selected
```
RagView        RagController
 │                │
 │ show()         │
 ├───────────────►│
 │                │
 │ get_rag_state()│
 ├───────────────►│
 │                │
 │                │ check current_rag_repository
 │                │ (is None)
 │                │
 │◄───────────────│ return None
 │                │
 │ display "No repo selected"
 │◄───────────────│
```

---

## Detailed Implementation

### RagController.get_rag_state()

```python
def get_rag_state(self) -> RagState | None:
    """
    Retrieve current repository state.
    
    Returns:
        RagState with repository information, or None if:
        - No repository selected
        - Repository inaccessible
        - Error retrieving state
    """
    # Check repository selected
    if not self.current_rag_repository:
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
        
        # Return state
        return RagState(
            url=url,
            data_base_location=data_base_path,
            documents_location=documents_path
        )
        
    except ImportError as e:
        print(f"Failed to import Rag class: {e}")
        return None
    except Exception as e:
        print(f"Error retrieving repository state: {e}")
        return None
```

### View State Display

```python
def _display_repository_state(self, state: RagState | None) -> None:
    """
    Display repository state in menu header.
    
    Args:
        state: Repository state or None
    """
    self._console.print("")
    self._console.print("═" * 50, style="bold")
    
    if state is None:
        # No repository selected
        self._console.print("⚠️  No repository selected", style="yellow")
        self._console.print("")
        self._console.print("Please select or create a repository to continue.", style="italic")
    else:
        # Repository selected
        repo_id = self._controller.current_rag_repository.id
        self._console.print(f"📁 {repo_id}", style="bold green")
        self._console.print("")
        
        # Show database location
        if state.data_base_location:
            self._console.print(f"   Database: {state.data_base_location}")
        else:
            self._console.print("   Database: Not initialized", style="italic")
        
        # Show documents location
        if state.documents_location:
            self._console.print(f"   Documents: {state.documents_location}")
        else:
            self._console.print("   Documents: No documents ingested", style="italic")
        
        # Show URL if available
        if state.url:
            self._console.print(f"   Ingested URL: {state.url}", style="cyan")
        else:
            self._console.print("   Status: Empty repository", style="italic")
    
    self._console.print("═" * 50, style="bold")
```

---

## Integration with Existing Code

### Changes to Rag Class (if needed)

**Verify:** Check if these methods exist in `src/agentx/model/rag/rag.py`

**If missing, add:**
```python
def database_exists(self) -> bool:
    """Check if SQLite database exists."""
    return os.path.exists(self.database_path)

def documents_exist(self) -> bool:
    """Check if documents file exists."""
    return os.path.exists(self.documents_path)

def get_ingested_url(self) -> str | None:
    """
    Get the most recently ingested URL.
    Returns None if no ingestion history.
    """
    if not self.database_exists():
        return None
    
    try:
        from agentx.model.rag.rag_db import RagDatabase
        db = RagDatabase(self.database_path)
        ingestions = db.get_all_ingestions()
        
        if ingestions:
            return ingestions[-1].url
        return None
    except Exception as e:
        print(f"Error retrieving ingested URL: {e}")
        return None
```

### Changes to RagDatabase (if needed)

**Verify:** Check if `get_all_ingestions()` exists in `src/agentx/model/rag/rag_db.py`

**If missing, add:**
```python
def get_all_ingestions(self) -> list:
    """
    Get all ingestion records.
    Returns list of ingestion objects/records.
    """
    cursor = self.conn.execute(
        "SELECT oid, url, timestamp FROM ingestion ORDER BY timestamp DESC"
    )
    rows = cursor.fetchall()
    
    # Return as list of dicts or objects
    return [
        {'oid': row[0], 'url': row[1], 'timestamp': row[2]}
        for row in rows
    ]
```

---

## Error Handling

### Error Scenarios

| Scenario | Detection | Response |
|----------|-----------|----------|
| No repository selected | `current_rag_repository is None` | Return None, show message |
| Rag import fails | ImportError | Log error, return None |
| Repository path invalid | FileNotFoundError | Log error, return None |
| Database corrupted | SQLite error | Log error, return partial state |
| Permission denied | PermissionError | Log error, return None |

### Graceful Degradation

```python
def get_rag_state(self) -> RagState | None:
    """Get state with graceful error handling."""
    if not self.current_rag_repository:
        return None
    
    try:
        rag = Rag(working_directory=self.current_rag_repository.path)
        
        # Try to get each piece of state independently
        data_base_path = None
        documents_path = None
        url = None
        
        try:
            if rag.database_exists():
                data_base_path = rag.vector_db_path
                url = rag.get_ingested_url()
        except Exception as e:
            print(f"Warning: Could not access database: {e}")
        
        try:
            if rag.documents_exist():
                documents_path = rag.documents_path
        except Exception as e:
            print(f"Warning: Could not access documents: {e}")
        
        # Return partial state if possible
        return RagState(
            url=url,
            data_base_location=data_base_path,
            documents_location=documents_path
        )
        
    except Exception as e:
        print(f"Error retrieving repository state: {e}")
        return None
```

---

## Testing Strategy

### Unit Tests

**Test 1: State Retrieval with Data**
```python
def test_get_rag_state_with_data():
    controller = RagController()
    controller.current_rag_repository = RagRepository(
        id="rag_test",
        path="/tmp/test_rag/rag_test"
    )
    
    # Create test data
    Path("/tmp/test_rag/rag_test/rag.db").parent.mkdir(parents=True)
    Path("/tmp/test_rag/rag_test/rag.db").touch()
    Path("/tmp/test_rag/rag_test/documents.jsonl").touch()
    
    state = controller.get_rag_state()
    
    assert state is not None
    assert state.data_base_location is not None
    assert state.documents_location is not None
    
    # Cleanup
    shutil.rmtree("/tmp/test_rag")
```

**Test 2: State Retrieval Empty Repository**
```python
def test_get_rag_state_empty():
    controller = RagController()
    controller.current_rag_repository = RagRepository(
        id="rag_empty",
        path="/tmp/test_rag/rag_empty"
    )
    
    # Create empty repo
    Path("/tmp/test_rag/rag_empty").mkdir(parents=True)
    
    state = controller.get_rag_state()
    
    assert state is not None
    assert state.data_base_location is None
    assert state.documents_location is None
    assert state.url is None
    
    # Cleanup
    shutil.rmtree("/tmp/test_rag")
```

**Test 3: No Repository Selected**
```python
def test_get_rag_state_no_repo():
    controller = RagController()
    controller.current_rag_repository = None
    
    state = controller.get_rag_state()
    
    assert state is None
```

### Integration Tests

**Test 1: Full Flow - Create → Select → View State**
```python
def test_full_state_flow():
    # Create repository
    creator = RagCreateRepositoryController("/tmp/test_flow")
    repo = creator.show()
    
    # Select repository
    selector = RagRepositorySelectionController("/tmp/test_flow")
    # Mock selection
    selector.view._selected_index = 1
    selector.get_repositories()
    selected = selector.get_selected_repository()
    
    # Set in controller
    controller = RagController()
    controller.current_rag_repository = selected
    
    # Get state
    state = controller.get_rag_state()
    
    assert state is not None
    assert state.data_base_location is not None
    
    # Cleanup
    shutil.rmtree("/tmp/test_flow")
```

---

## Performance Considerations

### State Retrieval Cost
- Database existence check: ~1ms
- Documents existence check: ~1ms
- URL retrieval from DB: ~5-10ms
- **Total:** ~10-20ms per call

### Caching Strategy
**Option 1:** Cache state in controller
- Pros: Fast subsequent calls
- Cons: May become stale

**Option 2:** Always re-read
- Pros: Always accurate
- Cons: Slight delay

**Recommendation:** Always re-read (cost is negligible, accuracy important)

---

## Future Enhancements

### 1. Repository Statistics
```python
def get_repository_stats(self) -> dict:
    """Get detailed repository statistics."""
    return {
        'document_count': self._count_documents(),
        'ingestion_count': self._count_ingestions(),
        'vector_count': self._count_vectors(),
        'last_ingestion': self._get_last_ingestion_date()
    }
```

### 2. State Change Events
Notify view when state changes:
```python
class RagController:
    def on_repository_selected(self, repo: RagRepository):
        self.current_rag_repository = repo
        self.view.on_state_changed()  # Trigger refresh
```

### 3. Path Shortening
Display relative paths when possible:
```python
def _shorten_path(self, path: str) -> str:
    """Convert absolute path to relative if under working directory."""
    try:
        return path.replace(self.rag_working_directory, "...")
    except:
        return path
```

---

*Created: 2026-06-21*
*Status: Design Complete - Ready for Implementation*