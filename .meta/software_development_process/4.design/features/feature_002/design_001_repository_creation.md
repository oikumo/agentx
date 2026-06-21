# DESIGN: RAG Repository Creation

## Overview
This document details the design for implementing repository creation functionality in the RAG system.

---

## Architecture

### Component Diagram
```
┌─────────────────────────────────────────────────────────────┐
│                    RAG Main Menu                             │
│                      (RagController)                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ user selects "Create Repository"
                     ▼
┌─────────────────────────────────────────────────────────────┐
│            Repository Creation Screen                        │
│         (RagCreateRepositoryController)                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              RagCreateRepositoryView                  │   │
│  │  - Displays prompt                                    │   │
│  │  - Captures user input                                │   │
│  │  - Shows validation errors                            │   │
│  │  - Shows success message                              │   │
│  └──────────────────────────────────────────────────────┘   │
│                          │                                   │
│                          ▼                                   │
│         ┌─────────────────────────────────┐                 │
│         │  Validation Logic                │                 │
│         │  - validate_repository_name()    │                 │
│         └─────────────────────────────────┘                 │
│                          │                                   │
│                          ▼                                   │
│         ┌─────────────────────────────────┐                 │
│         │  Creation Logic                  │                 │
│         │  - create_repository()           │                 │
│         │  - initialize_directory()        │                 │
│         │  - initialize_database()         │                 │
│         └─────────────────────────────────┘                 │
└─────────────────────────────────────────────────────────────┘
                     │
                     │ success
                     ▼
┌─────────────────────────────────────────────────────────────┐
│            Repository Selection Screen                       │
│         (RagRepositorySelectionController)                   │
│  - Shows updated repository list                             │
│  - Includes newly created repository                         │
└─────────────────────────────────────────────────────────────┘
```

---

## Class Design

### 1. RagCreateRepositoryView (NEW)

**Location:** `src/agentx/ui/screens/rag/rag_create_repository_view.py`

**Responsibilities:**
- Display repository name prompt
- Capture and validate user input (format only, not business logic)
- Show error messages
- Show success confirmation

**Interface:**
```python
class IRagCreateRepositoryViewPartner(ABC):
    """Abstract Partner Interface for Repository Creation View."""
    
    @abstractmethod
    def on_name_entered(self, name: str) -> bool:
        """Process entered name. Returns True if accepted."""
        pass
    
    @abstractmethod
    def get_prompt(self) -> str:
        """Return the prompt prefix for this screen."""
        pass
```

**Class Structure:**
```python
class RagCreateRepositoryView:
    def __init__(self, partner: IRagCreateRepositoryViewPartner):
        self._partner = partner
        self._console = UIConsole(self._partner.get_prompt())
        self._created_repository_name: str | None = None
    
    def show(self) -> str | None:
        """
        Display creation screen and return created repository name.
        Returns None if cancelled.
        """
        # Implementation in sequence diagram below
    
    def show_error(self, message: str) -> None:
        """Display error message."""
        pass
    
    def show_success(self, repository_name: str, path: str) -> None:
        """Display success message with repository details."""
        pass
```

---

### 2. RagCreateRepositoryController (EXTEND)

**Location:** `src/agentx/ui/screens/rag/rag_create_repository_controller.py`

**Current State:** Empty placeholder

**New Structure:**
```python
class RagCreateRepositoryController(IRagCreateRepositoryViewPartner):
    def __init__(self, working_directory: str):
        self._view = RagCreateRepositoryView(self)
        self._working_directory = working_directory
        self._created_repository: RagRepository | None = None
    
    def show(self) -> RagRepository | None:
        """
        Show repository creation screen.
        Returns created RagRepository or None if cancelled.
        """
        self._view.show()
        return self._created_repository
    
    def on_name_entered(self, name: str) -> bool:
        """
        Process entered repository name.
        Returns True if name is valid and creation succeeded.
        """
        # Validate name
        is_valid, error_message = self._validate_repository_name(name)
        if not is_valid:
            self._view.show_error(error_message)
            return False
        
        # Create repository
        repository = self._create_repository(name)
        if not repository:
            self._view.show_error("Failed to create repository")
            return False
        
        self._created_repository = repository
        self._view.show_success(repository.id, repository.path)
        return True
    
    def get_prompt(self) -> str:
        return "(create-repository)"
    
    def _validate_repository_name(self, name: str) -> tuple[bool, str]:
        """Validate repository name format and availability."""
        # Implementation details below
    
    def _create_repository(self, name: str) -> RagRepository | None:
        """Create repository directory and initialize database."""
        # Implementation details below
```

---

## Sequence Diagrams

### Main Success Scenario
```
User          RagView        RagController      RagCreateRepositoryController  RagCreateRepositoryView  FileSystem  RagDatabase
 │               │                │                          │                          │                │             │
 │ Select        │                │                          │                          │                │             │
 │ "Create Repo" │                │                          │                          │                │             │
 ├──────────────►│                │                          │                          │                │             │
 │               │ select_repo()  │                          │                          │                │             │
 │               ├───────────────►│                          │                          │                │             │
 │               │                │                          │                          │                │             │
 │               │                │ create_repository()      │                          │                │             │
 │               │                ├─────────────────────────►│                          │                │             │
 │               │                │                          │                          │                │             │
 │               │                │                          │ show()                   │                │             │
 │               │                │                          ├─────────────────────────►│                │             │
 │               │                │                          │                          │                │             │
 │               │                │                          │                          │ display prompt │             │
 │ Enter name    │                │                          │                          │◄───────────────│             │
 ├──────────────►│                │                          │                          │                │             │
 │               │ capture input  │                          │                          │                │             │
 │               ├───────────────►│                          │                          │                │             │
 │               │                │                          │                          │                │             │
 │               │                │ on_name_entered(name)    │                          │                │             │
 │               │                ├─────────────────────────►│                          │                │             │
 │               │                │                          │                          │                │             │
 │               │                │                          │ _validate_repository_name()              │             │
 │               │                │                          ├──────────────────────────────────────────►│             │
 │               │                │                          │                          │                │             │
 │               │                │                          │                          │ check format   │             │
 │               │                │                          │                          │ check exists   │             │
 │               │                │                          │◄──────────────────────────────────────────│             │
 │               │                │                          │                          │                │             │
 │               │                │                          │                          │ create dir     │             │
 │               │                │                          │                          ├───────────────►│             │
 │               │                │                          │                          │                │             │
 │               │                │                          │                          │                │ create db   │
 │               │                │                          │                          │                ├────────────►│
 │               │                │                          │                          │                │             │
 │               │                │                          │                          │ show success   │             │
 │               │                │                          │◄─────────────────────────│                │             │
 │               │                │                          │                          │                │             │
 │               │                │◄─────────────────────────│                          │                │             │
 │               │                │                          │                          │                │             │
 │               │ show_menu()    │                          │                          │                │             │
 │               │◄───────────────│                          │                          │                │             │
 │◄──────────────│                │                          │                          │                │             │
 │ Success message displayed     │                          │                          │                │             │
```

### Alternative Flow: Invalid Name
```
User          RagCreateRepositoryController  RagCreateRepositoryView
 │                          │                          │
 │ Enter invalid name       │                          │
 ├─────────────────────────►│                          │
 │                          │                          │
 │                          │ on_name_entered(name)    │
 │                          ├─────────────────────────►│
 │                          │                          │
 │                          │ _validate_repository_name()
 │                          │ (returns: False, "Invalid characters")
 │                          │                          │
 │                          │ show_error(message)      │
 │                          ├─────────────────────────►│
 │                          │                          │
 │                          │                          │ display error
 │◄─────────────────────────│                          │
 │ Error message displayed  │                          │
 │                          │                          │
 │ Re-enter name or cancel  │                          │
```

---

## Detailed Implementation

### Validation Logic

```python
def _validate_repository_name(self, name: str) -> tuple[bool, str]:
    """
    Validate repository name.
    Returns (True, "") if valid, (False, error_message) if invalid.
    """
    import re
    from pathlib import Path
    
    # Check empty
    if not name or not name.strip():
        return False, "Repository name cannot be empty"
    
    name = name.strip()
    
    # Check length
    if len(name) > 50:
        return False, "Repository name too long (max 50 characters)"
    
    # Check format (alphanumeric + underscore only)
    if not re.match(r'^[a-zA-Z0-9_]+$', name):
        return False, "Repository name contains invalid characters (use letters, numbers, underscore only)"
    
    # Check for prefix
    if name.startswith('rag_'):
        return False, "Repository name must not include 'rag_' prefix (added automatically)"
    
    # Check for path traversal
    if '..' in name or '/' in name or '\\' in name:
        return False, "Repository name contains invalid characters"
    
    # Check existence
    repo_path = Path(self._working_directory) / f"rag_{name}"
    if repo_path.exists():
        return False, f"Repository '{name}' already exists"
    
    return True, ""
```

### Repository Creation Logic

```python
def _create_repository(self, name: str) -> RagRepository | None:
    """
    Create repository directory and initialize database.
    Returns RagRepository on success, None on failure.
    """
    from pathlib import Path
    from agentx.model.rag.rag_repository import RagRepository
    from agentx.model.rag.rag_db import RagDatabase
    
    try:
        # Create directory
        repo_path = Path(self._working_directory) / f"rag_{name}"
        repo_path.mkdir(parents=True, exist_ok=False)
        
        # Initialize database
        db_path = repo_path / "rag.db"
        db = RagDatabase(str(db_path))
        db.initialize()  # Assumes RagDatabase has init method
        
        # Create repository object
        repository = RagRepository(
            id=f"rag_{name}",
            path=str(repo_path)
        )
        
        return repository
        
    except FileExistsError:
        return None
    except PermissionError:
        return None
    except Exception as e:
        # Log error
        print(f"Error creating repository: {e}")
        # Clean up partial creation
        if 'repo_path' in locals() and repo_path.exists():
            import shutil
            shutil.rmtree(repo_path, ignore_errors=True)
        return None
```

---

## View Implementation

### RagCreateRepositoryView

```python
from agentx.ui.common.ui_console import UIConsole
from abc import ABC, abstractmethod

class IRagCreateRepositoryViewPartner(ABC):
    """Abstract Partner Interface for Repository Creation View."""
    
    @abstractmethod
    def on_name_entered(self, name: str) -> bool:
        """Process entered name. Returns True if accepted."""
        pass
    
    @abstractmethod
    def get_prompt(self) -> str:
        """Return the prompt prefix for this screen."""
        pass

class RagCreateRepositoryView:
    def __init__(self, partner: IRagCreateRepositoryViewPartner):
        self._partner = partner
        self._console = UIConsole(self._partner.get_prompt())
    
    def show(self) -> None:
        """Display repository creation screen."""
        while True:
            self._console.print("")
            self._console.print("Enter repository name (without 'rag_' prefix):")
            self._console.print("  - Use letters, numbers, and underscores only")
            self._console.print("  - Maximum 50 characters")
            self._console.print("  - Type 'cancel' to abort")
            self._console.print("")
            
            name = self._console.capture_input("> ").strip()
            
            # Check cancellation
            if name.lower() in ['cancel', 'back', 'q', 'quit', '']:
                self._console.print("Repository creation cancelled.")
                return
            
            # Send to controller for validation and creation
            if self._partner.on_name_entered(name):
                # Success - repository created
                return
            # If we get here, validation failed - loop continues
    
    def show_error(self, message: str) -> None:
        """Display error message."""
        self._console.print("")
        self._console.print(f"❌ Error: {message}", style="red")
        self._console.print("")
    
    def show_success(self, repository_name: str, path: str) -> None:
        """Display success message."""
        self._console.print("")
        self._console.print(f"✅ Repository '{repository_name}' created successfully!", style="green")
        self._console.print(f"   Path: {path}")
        self._console.print("")
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

**No changes needed** - repository creation is separate flow

### Changes to RagView

**Location:** `src/agentx/ui/screens/rag/rag_view.py`

Add menu option for repository creation if not already present:
```python
def show(self):
    # ... existing code ...
    self._console.print("[1] Select Repository")
    self._console.print("[2] Create Repository")  # Add if missing
    self._console.print("[3] Web Ingestion")
    self._console.print("[4] RAG Chat")
    self._console.print("[5] Quit")
```

### Changes to RagController Command Handling

**Location:** `src/agentx/ui/screens/rag/rag_controller.py`

Add handler for "Create Repository" option:
```python
def handle_menu_selection(self, selection: str) -> None:
    if selection == "1":
        self.select_repository()
    elif selection == "2":
        self.create_repository()  # New method
    elif selection == "3":
        self.show_web_ingestion()
    elif selection == "4":
        self.show_chat()
    elif selection in ["q", "quit", "exit"]:
        self.close()
```

Add new method:
```python
def create_repository(self) -> None:
    """Create new repository."""
    from agentx.ui.screens.rag.rag_create_repository_controller import RagCreateRepositoryController
    
    creator = RagCreateRepositoryController(self.rag_working_directory)
    new_repo = creator.show()
    
    if new_repo:
        self._console.print("Repository created. Please select it to use.")
        # Optionally auto-select:
        # self.current_rag_repository = new_repo
```

---

## Testing Strategy

### Unit Tests

**Test 1: Valid Repository Name**
```python
def test_create_valid_repository():
    controller = RagCreateRepositoryController("/tmp/test_rag")
    is_valid, error = controller._validate_repository_name("test_repo")
    assert is_valid == True
    assert error == ""
```

**Test 2: Invalid Name - Empty**
```python
def test_reject_empty_name():
    controller = RagCreateRepositoryController("/tmp/test_rag")
    is_valid, error = controller._validate_repository_name("")
    assert is_valid == False
    assert "cannot be empty" in error
```

**Test 3: Invalid Name - Special Characters**
```python
def test_reject_special_chars():
    controller = RagCreateRepositoryController("/tmp/test_rag")
    is_valid, error = controller._validate_repository_name("test@repo")
    assert is_valid == False
    assert "invalid characters" in error
```

**Test 4: Invalid Name - Already Exists**
```python
def test_reject_existing():
    controller = RagCreateRepositoryController("/tmp/test_rag")
    # Create directory first
    Path("/tmp/test_rag/rag_existing").mkdir(parents=True)
    is_valid, error = controller._validate_repository_name("existing")
    assert is_valid == False
    assert "already exists" in error
```

### Integration Tests

**Test 1: Full Creation Flow**
```python
def test_full_creation_flow():
    # Setup
    working_dir = "/tmp/test_rag_full"
    Path(working_dir).mkdir(parents=True, exist_ok=True)
    
    # Create repository
    controller = RagCreateRepositoryController(working_dir)
    repository = controller._create_repository("test_repo")
    
    # Verify
    assert repository is not None
    assert repository.id == "rag_test_repo"
    assert Path(repository.path).exists()
    assert (Path(repository.path) / "rag.db").exists()
    
    # Cleanup
    shutil.rmtree(working_dir)
```

---

## Error Handling

### Error Types and Responses

| Error Type | Detection Point | User Message | Recovery |
|------------|----------------|--------------|----------|
| Empty name | Validation | "Repository name cannot be empty" | Re-enter name |
| Invalid characters | Validation | "Invalid characters (use letters, numbers, underscore only)" | Re-enter name |
| Name too long | Validation | "Name too long (max 50 characters)" | Re-enter shorter name |
| Already exists | Validation | "Repository '{name}' already exists" | Choose different name |
| Path traversal | Validation | "Invalid characters in name" | Re-enter name |
| Directory creation fails | Creation | "Failed to create repository directory" | Check permissions, retry |
| Database init fails | Creation | "Failed to initialize database" | Check permissions, retry |
| Permission denied | Creation | "Permission denied" | Run with correct permissions |

### Cleanup on Failure

If directory creation succeeds but database initialization fails:
```python
try:
    repo_path.mkdir(parents=True)
    db = RagDatabase(str(repo_path / "rag.db"))
    db.initialize()
except Exception as e:
    # Clean up partial creation
    if repo_path.exists():
        shutil.rmtree(repo_path, ignore_errors=True)
    return None
```

---

## Dependencies

### New Files to Create
1. `src/agentx/ui/screens/rag/rag_create_repository_view.py`
2. Update `src/agentx/ui/screens/rag/rag_create_repository_controller.py`
3. Update `src/agentx/ui/screens/rag/rag_view.py` (add menu option)
4. Update `src/agentx/ui/screens/rag/rag_controller.py` (add handler)

### Existing Classes Used
- `RagRepository` (dataclass)
- `RagDatabase` (database initialization)
- `UIConsole` (UI rendering)
- `SessionController` (working directory)

### No New External Dependencies
All functionality uses existing libraries and stdlib.

---

*Created: 2026-06-21*
*Status: Design Complete - Ready for Implementation*