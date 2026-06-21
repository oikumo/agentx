# DESIGN: RAG Repository Selection

## Overview
This document details the design for fixing repository selection functionality to properly return the selected repository.

---

## Architecture

### Component Diagram
```
┌─────────────────────────────────────────────────────────────┐
│                    RAG Main Menu                             │
│                      (RagController)                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ user selects "Select Repository"
                     ▼
┌─────────────────────────────────────────────────────────────┐
│            Repository Selection Screen                       │
│         (RagRepositorySelectionController)                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │          RagRepositorySelectionView                   │   │
│  │  - Queries RagProvider for repositories              │   │
│  │  - Filters valid repositories (have rag.db)          │   │
│  │  - Displays numbered list                            │   │
│  │  - Captures user selection (index)                   │   │
│  │  - Stores selected index internally                  │   │
│  └──────────────────────────────────────────────────────┘   │
│                          │                                   │
│                          ▼                                   │
│         ┌─────────────────────────────────┐                 │
│         │  get_selected_repository()       │                 │
│         │  - Read selected index from view │                 │
│         │  - Map to RagRepository object   │                 │
│         │  - Validate repository           │                 │
│         │  - Return repository or None     │                 │
│         └─────────────────────────────────┘                 │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ returns RagRepository
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    RAG Main Menu                             │
│                      (RagController)                         │
│  - Stores repository in current_rag_repository               │
│  - Calls get_rag_state() to display info                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Class Design Changes

### 1. RagRepositorySelectionView (EXTEND)

**Location:** `src/agentx/ui/screens/rag/rag_repostitory_selection_view.py`

**Current State:** Unknown - needs verification

**Required Additions:**
```python
class RagRepositorySelectionView:
    def __init__(self, partner: IRagRepositorySelectionViewPartner):
        self._partner = partner
        self._console = UIConsole(self._partner.get_prompt())
        self._selected_index: int | None = None  # NEW: Store selection
    
    def show(self) -> None:
        """Display repository list and capture selection."""
        repositories = self._partner.get_repositories()
        
        if not repositories:
            self._console.print("No repositories found.")
            return
        
        # Display list
        for idx, repo_id in enumerate(repositories, 1):
            self._console.print(f"[{idx}] {repo_id}")
        
        # Capture selection
        while True:
            user_input = self._console.capture_input("Select repository (1-{count}) or 'cancel': ")
            
            # Check cancellation
            if user_input.lower() in ['cancel', 'back', 'q', 'quit']:
                self._selected_index = None
                return
            
            # Parse index
            try:
                index = int(user_input)
                if 1 <= index <= len(repositories):
                    self._selected_index = index  # Store selection
                    return
                else:
                    self._console.print(f"Invalid selection. Enter 1-{len(repositories)}")
            except ValueError:
                self._console.print("Invalid input. Please enter a number.")
    
    def get_selected_index(self) -> int | None:  # NEW: Getter for controller
        """Return the selected index (1-based) or None if cancelled."""
        return self._selected_index
```

---

### 2. RagRepositorySelectionController (EXTEND)

**Location:** `src/agentx/ui/screens/rag/rag_repository_selection_controller.py`

**Current State:** `get_selected_repository()` returns `None`

**New Implementation:**
```python
class RagRepositorySelectionController:
    def __init__(self, rag_working_directory: str):
        self.view = RagRepositorySelectionView(self)
        self.rag_provider = RagProvider(rag_working_directory)
        self._cached_repositories: list[RagRepository] | None = None
    
    def show(self) -> None:
        self.view.show()
    
    def get_repositories(self) -> list[str] | None:
        """Get list of valid repository IDs for display."""
        repositories = self.rag_provider.get_repositories()
        if not repositories:
            return None
        
        # Filter valid repositories and cache for later retrieval
        self._cached_repositories = [
            repo for repo in repositories 
            if self._validate_repository(repo)
        ]
        
        return [repo.id for repo in self._cached_repositories]
    
    def createRepository(self) -> None:
        new_repository = RagCreateRepositoryController()
        new_repository.show()
    
    def get_selected_repository(self) -> RagRepository | None:  # FIX THIS
        """
        Return the repository selected by user.
        Returns None if no selection or cancelled.
        """
        selected_index = self.view.get_selected_index()
        
        if selected_index is None:
            return None
        
        # Map 1-based index to 0-based list index
        list_index = selected_index - 1
        
        if not self._cached_repositories:
            return None
        
        if list_index < 0 or list_index >= len(self._cached_repositories):
            return None
        
        return self._cached_repositories[list_index]
    
    def _validate_repository(self, repository: RagRepository) -> bool:
        """
        Validate repository integrity.
        Returns True if repository is valid.
        """
        from pathlib import Path
        
        repo_path = Path(repository.path)
        
        # Check directory exists
        if not repo_path.exists():
            return False
        
        # Check rag.db exists
        db_path = repo_path / "rag.db"
        if not db_path.exists():
            return False
        
        # Check database is readable
        try:
            # Try to open database
            import sqlite3
            conn = sqlite3.connect(str(db_path))
            conn.execute("SELECT 1")
            conn.close()
        except Exception:
            return False
        
        return True
    
    def close(self):
        self._cached_repositories = None
```

---

## Sequence Diagrams

### Main Success Scenario
```
User          RagView        RagController      RagRepositorySelectionController  RagRepositorySelectionView  RagProvider
 │               │                │                          │                          │                │
 │ Select        │                │                          │                          │                │
 │ "Select Repo" │                │                          │                          │                │
 ├──────────────►│                │                          │                          │                │
 │               │ select_repo()  │                          │                          │                │
 │               ├───────────────►│                          │                          │                │
 │               │                │                          │                          │                │
 │               │                │ show()                   │                          │                │
 │               │                ├─────────────────────────►│                          │                │
 │               │                │                          │                          │                │
 │               │                │                          │ get_repositories()       │                │
 │               │                │                          ├─────────────────────────►│                │
 │               │                │                          │                          │                │
 │               │                │                          │                          │ get_repositories()
 │               │                │                          │                          ├───────────────►│
 │               │                │                          │                          │                │
 │               │                │                          │                          │◄───────────────│
 │               │                │                          │                          │ return list    │
 │               │                │                          │                          │                │
 │               │                │                          │ filter_valid()           │                │
 │               │                │                          │ cache results            │                │
 │               │                │                          │                          │                │
 │               │                │                          │ display_list(ids)        │                │
 │               │                │                          ├─────────────────────────►│                │
 │               │                │                          │                          │                │
 │               │                │                          │                          │ display list   │
 │◄──────────────│                │                          │                          │                │
 │ Enter index   │                │                          │                          │                │
 ├──────────────►│                │                          │                          │                │
 │               │ capture input  │                          │                          │                │
 │               ├───────────────►│                          │                          │                │
 │               │                │                          │                          │                │
 │               │                │                          │ store_index(index)       │                │
 │               │                │                          │◄─────────────────────────│                │
 │               │                │                          │                          │                │
 │               │                │◄─────────────────────────│                          │                │
 │               │                │                          │                          │                │
 │               │                │ get_selected_repository()│                          │                │
 │               │                ├─────────────────────────►│                          │                │
 │               │                │                          │                          │                │
 │               │                │                          │ read index from view     │                │
 │               │                │                          │ map to repository        │                │
 │               │                │                          │                          │                │
 │               │                │◄─────────────────────────│                          │                │
 │               │                │ repository object        │                          │                │
 │◄──────────────│                │                          │                          │                │
 │ Repository selected           │                          │                          │                │
```

### Alternative Flow: No Repositories
```
User          RagRepositorySelectionController  RagRepositorySelectionView
 │                          │                          │
 │ Select repository        │                          │
 ├─────────────────────────►│                          │
 │                          │                          │
 │                          │ get_repositories()       │
 │                          ├─────────────────────────►│
 │                          │                          │
 │                          │                          │ query provider
 │                          │                          │ (returns empty list)
 │                          │                          │
 │                          │ display_message()        │
 │                          ├─────────────────────────►│
 │                          │                          │
 │                          │                          │ "No repositories found"
 │◄─────────────────────────│                          │
 │ Message displayed        │                          │
```

### Alternative Flow: Invalid Selection
```
User          RagRepositorySelectionView
 │                          │
 │ Enter invalid index (e.g., "99")
 ├─────────────────────────►│
 │                          │
 │                          │ validate index
 │                          │ (out of range)
 │                          │
 │                          │ show error
 │                          │ "Invalid selection"
 │◄─────────────────────────│
 │ Re-enter selection       │
```

---

## Detailed Implementation

### View Selection Storage

**Key Design Decision:** View stores selected index, not repository object

**Rationale:**
- View only handles presentation layer
- Controller owns business logic (repository objects)
- Controller caches repository list for mapping
- Avoids coupling view to domain model

**Implementation:**
```python
class RagRepositorySelectionView:
    def __init__(self, partner: IRagRepositorySelectionViewPartner):
        self._partner = partner
        self._console = UIConsole(self._partner.get_prompt())
        self._selected_index: int | None = None  # 1-based index
    
    def show(self) -> None:
        """Show repository selection UI."""
        repositories = self._partner.get_repositories()
        
        if not repositories:
            self._console.print("No repositories found.")
            self._selected_index = None
            return
        
        self._console.print("")
        self._console.print("Available RAG Repositories:")
        self._console.print("─" * 40)
        
        for idx, repo_id in enumerate(repositories, 1):
            self._console.print(f"[{idx}] {repo_id}")
        
        self._console.print("─" * 40)
        
        while True:
            user_input = self._console.capture_input(
                f"Select repository (1-{len(repositories)}) or 'cancel': "
            ).strip()
            
            # Handle cancellation
            if user_input.lower() in ['cancel', 'back', 'q', 'quit', '']:
                self._console.print("Repository selection cancelled.")
                self._selected_index = None
                return
            
            # Validate and store selection
            try:
                index = int(user_input)
                if 1 <= index <= len(repositories):
                    self._selected_index = index
                    return
                else:
                    self._console.print(f"Invalid selection. Enter 1-{len(repositories)}")
            except ValueError:
                self._console.print("Invalid input. Please enter a number.")
    
    def get_selected_index(self) -> int | None:
        """Return selected index (1-based) or None."""
        return self._selected_index
```

### Controller Repository Mapping

**Key Design Decision:** Controller caches repository list for efficient mapping

**Rationale:**
- Avoids re-querying provider on every `get_selected_repository()` call
- Ensures consistency between displayed list and returned object
- Allows validation before display

**Implementation:**
```python
class RagRepositorySelectionController:
    def __init__(self, rag_working_directory: str):
        self.view = RagRepositorySelectionView(self)
        self.rag_provider = RagProvider(rag_working_directory)
        self._cached_repositories: list[RagRepository] | None = None
    
    def get_repositories(self) -> list[str] | None:
        """Get repository IDs for display, cache objects."""
        all_repos = self.rag_provider.get_repositories()
        if not all_repos:
            self._cached_repositories = None
            return None
        
        # Filter and cache
        self._cached_repositories = [
            repo for repo in all_repos 
            if self._validate_repository(repo)
        ]
        
        if not self._cached_repositories:
            return None
        
        return [repo.id for repo in self._cached_repositories]
    
    def get_selected_repository(self) -> RagRepository | None:
        """Map view selection to repository object."""
        selected_index = self.view.get_selected_index()
        
        # Check if selection was made
        if selected_index is None:
            return None
        
        # Check if cache exists
        if not self._cached_repositories:
            return None
        
        # Map 1-based index to 0-based list
        list_index = selected_index - 1
        
        # Bounds check
        if list_index < 0 or list_index >= len(self._cached_repositories):
            return None
        
        return self._cached_repositories[list_index]
```

### Repository Validation

**Validation Criteria:**
1. Directory exists
2. `rag.db` exists
3. Database is readable (can connect)
4. (Optional) Vector store directory exists

**Implementation:**
```python
def _validate_repository(self, repository: RagRepository) -> bool:
    """Validate repository integrity."""
    from pathlib import Path
    import sqlite3
    
    repo_path = Path(repository.path)
    
    # Check directory exists
    if not repo_path.exists() or not repo_path.is_dir():
        print(f"Repository directory not found: {repo_path}")
        return False
    
    # Check rag.db exists
    db_path = repo_path / "rag.db"
    if not db_path.exists():
        print(f"Repository database not found: {db_path}")
        return False
    
    # Check database is accessible
    try:
        conn = sqlite3.connect(str(db_path))
        # Try to query ingestion table
        conn.execute("SELECT COUNT(*) FROM ingestion")
        conn.close()
    except sqlite3.Error as e:
        print(f"Database error for {repository.id}: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error validating {repository.id}: {e}")
        return False
    
    return True
```

---

## Integration with Existing Code

### Changes to RagController

**Location:** `src/agentx/ui/screens/rag/rag_controller.py`

**Current:**
```python
def select_repository(self):
    repository_selection = RagRepositorySelectionController(self.rag_working_directory)
    repository_selection.show()
    self.current_rag_repository = repository_selection.get_selected_repository()
```

**No changes needed** - already calls `get_selected_repository()`, just needs implementation

**After selection, should update state display:**
```python
def select_repository(self):
    repository_selection = RagRepositorySelectionController(self.rag_working_directory)
    repository_selection.show()
    self.current_rag_repository = repository_selection.get_selected_repository()
    
    if self.current_rag_repository:
        self._console.print(f"Selected repository: {self.current_rag_repository.id}")
    else:
        self._console.print("No repository selected.")
```

### Changes to RagProvider

**Location:** `src/agentx/model/rag/rag_provider.py`

**Verify:** `get_repositories()` returns list of `RagRepository` objects

**Expected:**
```python
def get_repositories(self) -> list[RagRepository]:
    """Discover and return all valid repositories."""
    repositories = []
    # ... discovery logic ...
    return repositories
```

---

## Error Handling

### Error Scenarios

| Scenario | Detection | Response |
|----------|-----------|----------|
| No repositories | Provider returns empty list | Display "No repositories found" |
| All repositories invalid | Filter removes all | Display "No valid repositories found" |
| User cancels | View detects cancel command | Return None |
| Invalid index | Index out of range | Show error, re-prompt |
| Non-numeric input | Parse error | Show error, re-prompt |
| Repository corrupted | Validation fails | Skip from list, log warning |

### Graceful Degradation

If repository validation fails:
```python
def get_repositories(self) -> list[str] | None:
    all_repos = self.rag_provider.get_repositories()
    if not all_repos:
        return None
    
    valid_repos = []
    for repo in all_repos:
        if self._validate_repository(repo):
            valid_repos.append(repo)
        else:
            # Log but don't crash
            print(f"Skipping invalid repository: {repo.id}")
    
    self._cached_repositories = valid_repos
    
    if not valid_repos:
        return None
    
    return [repo.id for repo in valid_repos]
```

---

## Testing Strategy

### Unit Tests

**Test 1: Valid Selection**
```python
def test_get_selected_repository_valid():
    controller = RagRepositorySelectionController("/tmp/test_rag")
    # Mock view to return index 1
    controller.view._selected_index = 1
    # Mock cache
    controller._cached_repositories = [RagRepository(id="rag_test", path="/tmp/test")]
    
    result = controller.get_selected_repository()
    
    assert result is not None
    assert result.id == "rag_test"
```

**Test 2: Cancelled Selection**
```python
def test_get_selected_repository_cancelled():
    controller = RagRepositorySelectionController("/tmp/test_rag")
    controller.view._selected_index = None
    
    result = controller.get_selected_repository()
    
    assert result is None
```

**Test 3: Invalid Index**
```python
def test_get_selected_repository_invalid_index():
    controller = RagRepositorySelectionController("/tmp/test_rag")
    controller.view._selected_index = 99  # Out of range
    controller._cached_repositories = [RagRepository(id="rag_test", path="/tmp/test")]
    
    result = controller.get_selected_repository()
    
    assert result is None
```

**Test 4: Repository Validation**
```python
def test_validate_repository_valid():
    controller = RagRepositorySelectionController("/tmp/test_rag")
    repo = RagRepository(id="rag_test", path="/tmp/test_rag/rag_test")
    
    # Create test structure
    Path(repo.path).mkdir(parents=True)
    (Path(repo.path) / "rag.db").touch()
    
    result = controller._validate_repository(repo)
    
    assert result == True
    
    # Cleanup
    shutil.rmtree("/tmp/test_rag")
```

### Integration Tests

**Test 1: Full Selection Flow**
```python
def test_full_selection_flow():
    # Setup
    working_dir = "/tmp/test_rag_select"
    Path(working_dir).mkdir(parents=True)
    
    # Create test repository
    repo_path = Path(working_dir) / "rag_test"
    repo_path.mkdir()
    (repo_path / "rag.db").touch()
    
    # Test selection
    controller = RagRepositorySelectionController(working_dir)
    
    # Mock user selection
    controller.view._selected_index = 1
    
    # Get repositories (populates cache)
    repos = controller.get_repositories()
    assert repos is not None
    assert len(repos) == 1
    
    # Get selected
    selected = controller.get_selected_repository()
    assert selected is not None
    assert selected.id == "rag_test"
    
    # Cleanup
    shutil.rmtree(working_dir)
```

---

## Performance Considerations

### Caching Strategy
- Cache repository list in controller
- Clear cache on `close()`
- Re-populate on `show()`

**Rationale:** Repository list doesn't change during single selection session

### Validation Cost
- Database validation: ~1-5ms per repository
- Acceptable for <100 repositories
- For large numbers, consider lazy validation

---

## Future Enhancements

### 1. Repository Metadata Display
Show additional info in selection list:
```
[1] rag_project_alpha    (3 documents, last updated: 2026-06-20)
[2] rag_research_notes   (15 documents, last updated: 2026-06-21)
```

### 2. Repository Search/Filter
For large repository lists:
```
Enter repository name to filter (or number to select):
```

### 3. Automatic Cleanup
Option to remove invalid repositories from disk:
```
Found 2 invalid repositories. Remove them? (y/N)
```

---

*Created: 2026-06-21*
*Status: Design Complete - Ready for Implementation*