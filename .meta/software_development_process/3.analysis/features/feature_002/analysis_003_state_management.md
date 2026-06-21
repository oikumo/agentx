# ANALYSIS: RAG State Management

## Use Case: Display RAG Repository State

### Primary Actor
- User

### Preconditions
- A repository has been selected (`RagController.current_rag_repository` is set)
- User is viewing RAG main menu
- Repository contains valid data (database, vector store)

### Main Flow
1. User enters RAG main menu
2. System checks if repository is selected
3. System calls `get_rag_state()` to retrieve repository information
4. System queries `Rag` instance for:
   - Site URL (if web ingestion was performed)
   - Database path
   - Documents path
5. System formats state information for display
6. System displays repository state in menu header or status area
7. User can proceed with operations (chat, ingestion, etc.)

### Alternative Flows

#### A1: No Repository Selected
- 2a. System detects `current_rag_repository` is None
- 2b. System displays: "No repository selected"
- 2c. System prompts user to select or create repository
- 2d. Skip state display

#### A2: Repository Has No Data
- 4a. System detects empty repository (no ingestion history)
- 4b. System displays: "Repository is empty - no data ingested yet"
- 4c. Show database and documents paths only
- 4d. Continue to step 7

#### A3: Repository Data Inaccessible
- 4a. System cannot access database or vector store
- 4b. System displays warning: "Repository data may be corrupted"
- 4c. Show paths but mark as inaccessible
- 4d. Allow user to proceed with caution

### Postconditions
- User sees current repository state
- State information is accurate and up-to-date
- User can make informed decisions about next actions

---

## Domain Concepts

### Classes Involved
- `RagController` - manages state retrieval
- `Rag` - main orchestrator providing state data
- `RagState` (dataclass) - state container
- `RagRepository` - repository metadata

### State Components
```python
@dataclass
class RagState:
    url: str | None                    # Website URL (if ingested)
    data_base_location: str | None     # Path to rag.db
    documents_location: str | None     # Path to documents.jsonl
```

---

## Data Requirements

### State Information to Display

#### 1. Repository Name
- Source: `RagRepository.id`
- Format: `rag_{name}`
- Always available

#### 2. Repository Path
- Source: `RagRepository.path`
- Format: Full filesystem path
- Always available

#### 3. Database Location
- Source: `Rag.vector_db_path` or constructed from repository path
- Format: `{repo_path}/rag.db`
- Available if repository initialized

#### 4. Documents Location
- Source: `Rag.documents_path`
- Format: `{repo_path}/documents.jsonl`
- Available if documents exist

#### 5. Ingested URL
- Source: `Rag.site_url` or from `RagDatabase` ingestion history
- Format: Full URL string
- Available if web ingestion performed

#### 6. Document Count (Optional Enhancement)
- Source: `RagDatabase.get_ingestion_count()` or count from JSONL
- Format: Integer
- Available if data exists

---

## Operations Extracted

### 1. `get_rag_state() -> RagState | None`
**Location:** `RagController`
**Purpose:** Retrieve current repository state for display

**Current Status:** Returns `None` (implementation commented out)

**Preconditions:**
- `current_rag_repository` is not None
- Repository directory exists
- Repository is accessible

**Exceptions:**
- No repository selected → return None
- Repository inaccessible → return None or partial state
- `Rag` instance not initialized → initialize or return None

**Postconditions:**
- Returns `RagState` with available information
- Returns `None` if no repository selected
- Does not modify repository state

### 2. `initialize_rag_instance(repository: RagRepository) -> Rag`
**Location:** `RagController` (new method or inline)
**Purpose:** Create `Rag` instance for selected repository

**Preconditions:**
- Repository object is valid
- Repository directory exists

**Exceptions:**
- Invalid repository → raise ValueError
- Directory not found → raise FileNotFoundError

**Postconditions:**
- Returns initialized `Rag` instance
- `Rag` is configured with correct paths

### 3. `format_state_display(state: RagState) -> str`
**Location:** `RagController` or `RagView` (new method)
**Purpose:** Format state for user display

**Preconditions:**
- State object exists (may have None fields)

**Exceptions:**
- None

**Postconditions:**
- Returns formatted string for display
- Handles None values gracefully

---

## UI Behavior Specification

### Display Format
```
RAG Repository: rag_project_alpha
Path: /home/user/agentx_data/rag_project_alpha
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Database: /home/user/agentx_data/rag_project_alpha/rag.db
Documents: /home/user/agentx_data/rag_project_alpha/documents.jsonl
Ingested URL: https://example.com/docs
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[1] Select Repository
[2] Web Ingestion
[3] RAG Chat
[4] Quit
```

### Empty Repository Display
```
RAG Repository: rag_new_project
Path: /home/user/agentx_data/rag_new_project
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Status: Empty repository - no data ingested yet
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[1] Select Repository
[2] Web Ingestion
[3] RAG Chat
[4] Quit
```

### No Repository Selected Display
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
No repository selected
Please select or create a repository to continue
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[1] Select Repository
[2] Create Repository
[3] Quit
```

---

## Current Implementation Issues

### Issue 1: `get_rag_state()` Returns None
**Location:** `rag_controller.py:49-67`
**Problem:** Method has commented-out implementation

**Commented Code:**
```python
return None
"""
data_base_path = None
documents_path = None
if self.rag.is_data():
    data_base_path = self.rag.vector_db_path
    documents_path = self.rag.documents_path

return RagState(
    url=self.rag.site_url,
    data_base_location=data_base_path,
    documents_location=documents_path
)
"""
```

**Problems with Commented Code:**
1. References `self.rag` which doesn't exist in `RagController`
2. Should use `self.current_rag_repository` to create `Rag` instance
3. `is_data()` method may not exist on `Rag` class
4. Doesn't handle case where repository exists but has no data

**Fix Required:**
- Create `Rag` instance from selected repository
- Check for data existence properly
- Return partial state if some fields unavailable
- Handle errors gracefully

### Issue 2: No `Rag` Instance in Controller
**Problem:** `RagController` doesn't maintain `Rag` instance
**Fix Required:**
- Add `current_rag: Rag | None` field
- Initialize when repository selected
- Or create on-demand in `get_rag_state()`

**Recommendation:** Create on-demand to avoid stale state

### Issue 3: State Not Displayed in View
**Problem:** Even if state retrieved, view may not display it
**Fix Required:**
- Verify `RagView` has method to display state
- Update view to show state in menu header

---

## Integration Points

### Rag Class
- Need to verify `Rag` class provides:
  - `vector_db_path` property
  - `documents_path` property
  - `site_url` property
  - Method to check if data exists

### RagDatabase
- May need to query for ingestion history
- Provides URL of ingested site

### RagView
- Must display state information
- Should format paths nicely (relative vs absolute)

---

## Constraints

### Performance
- State retrieval should be fast (no heavy I/O)
- Don't load vector store just to get state
- Query SQLite only if necessary

### Accuracy
- State must reflect current repository state
- Don't cache stale information
- Re-read from disk/database each time

### Usability
- Display paths in user-friendly format
- Show meaningful status messages
- Handle missing data gracefully

---

## Open Questions

1. Should state include vector store statistics (document count, embeddings count)?
   - **Recommendation:** Not for v1 - requires loading vector store

2. Should we cache state or always re-read?
   - **Recommendation:** Always re-read for accuracy

3. What if repository was modified externally?
   - **Recommendation:** Always read from disk - will reflect external changes

4. Should state include last ingestion timestamp?
   - **Recommendation:** Yes - useful metadata, can get from `rag.db`

---

## Design Recommendations

### 1. On-Demand Rag Instance
```python
def _get_rag_instance(self) -> Rag | None:
    """Create Rag instance for current repository."""
    if not self.current_rag_repository:
        return None
    return Rag(working_directory=self.current_rag_repository.path)
```

### 2. Robust State Retrieval
```python
def get_rag_state(self) -> RagState | None:
    """Get current repository state."""
    if not self.current_rag_repository:
        return None
    
    try:
        rag = self._get_rag_instance()
        if not rag:
            return None
        
        # Check what data exists
        has_db = rag.database_exists()
        has_docs = rag.documents_exist()
        
        return RagState(
            url=rag.site_url if has_db else None,
            data_base_location=rag.vector_db_path if has_db else None,
            documents_location=rag.documents_path if has_docs else None
        )
    except Exception as e:
        # Log error, return None
        return None
```

### 3. View Integration
```python
def show(self):
    """Show main menu with state."""
    state = self._controller.get_rag_state()
    self._display_header(state)
    self._display_menu()
```

---

*Created: 2026-06-21*
*Status: Analysis Complete - Ready for Design*