# ANALYSIS: RAG Repository Selection

## Use Case: Select Existing RAG Repository

### Primary Actor
- User

### Preconditions
- User is in RAG main menu
- At least one repository exists in working directory
- User has selected "Select Repository" option

### Main Flow
1. User selects "Select Repository" from RAG main menu
2. System queries `RagProvider` for available repositories
3. System filters repositories (must have `rag.db` file)
4. System displays list of available repositories
5. User selects repository from list
6. System validates repository integrity:
   - Directory exists
   - `rag.db` exists
   - Vector store directory exists (optional - may be empty)
7. System loads repository metadata
8. System returns selected `RagRepository` object to caller
9. System displays confirmation message
10. System returns to RAG main menu with repository state displayed

### Alternative Flows

#### A1: No Repositories Available
- 2a. System finds no repositories
- 2b. System displays message: "No repositories found"
- 2c. System offers to create new repository
- 2d. Return to RAG main menu

#### A2: Invalid Repository Selected
- 6a. System detects missing or corrupted repository
- 6b. System displays error: "Repository '{name}' is corrupted or incomplete"
- 6c. System offers to remove from list or skip
- 6d. Return to step 4

#### A3: User Cancels Selection
- 4a. User enters cancel command (e.g., "cancel", "back", "q")
- 4b. System displays "Repository selection cancelled"
- 4c. Return to RAG main menu without selection

### Postconditions
- `RagController.current_rag_repository` is set to selected repository
- RAG main menu displays repository state (URL, database path, documents path)
- User can proceed with web ingestion or chat operations

---

## Domain Concepts

### Classes Involved
- `RagRepositorySelectionController` - orchestrates selection flow
- `RagRepositorySelectionView` - displays repository list
- `RagProvider` - discovers repositories
- `RagRepository` - data structure for repository
- `RagController` - receives selected repository

### Data Flow
```
User Selection (index)
    ↓
RagRepositorySelectionView
    ↓
RagRepositorySelectionController
    ↓
RagProvider.get_repositories()
    ↓
RagRepository object
    ↓
RagController.current_rag_repository
```

---

## UI Requirements

### Display Format
```
Available RAG Repositories:
---------------------------
[1] rag_project_alpha
[2] rag_research_notes
[3] rag_documentation
---------------------------
Select repository (1-3) or 'cancel':
```

### Input Handling
- Numeric selection (1, 2, 3, etc.)
- Cancel command ("cancel", "back", "q", "quit")
- Invalid input handling (out of range, non-numeric)

### Validation
- Repository must exist on disk
- Repository must contain `rag.db`
- Repository must be readable

---

## Operations Extracted

### 1. `get_selected_repository() -> RagRepository | None`
**Location:** `RagRepositorySelectionController`
**Purpose:** Return the repository selected by user

**Current Status:** Returns `None` (not implemented)

**Preconditions:**
- View has been shown
- User has made a selection
- Repositories have been loaded via `RagProvider`

**Exceptions:**
- No selection made → return None
- Invalid selection → return None
- Repository validation fails → return None

**Postconditions:**
- Returns valid `RagRepository` object on success
- Returns `None` on cancellation or error
- Updates internal selection state

### 2. `validate_repository(repository: RagRepository) -> bool`
**Location:** `RagRepositorySelectionController` (new method)
**Purpose:** Verify repository integrity before returning

**Preconditions:**
- Repository object exists

**Exceptions:**
- None - validation handles all cases

**Postconditions:**
- Returns True if repository is valid
- Returns False if corrupted or incomplete

### 3. `filter_valid_repositories(repositories: list[RagRepository]) -> list[RagRepository]`
**Location:** `RagRepositorySelectionController` (new method)
**Purpose:** Filter out invalid repositories from list

**Preconditions:**
- List of repository objects exists

**Exceptions:**
- None

**Postconditions:**
- Returns list containing only valid repositories
- Logs or reports filtered repositories

---

## UI Behavior Specification

### View-Controller Interaction
```
RagRepositorySelectionController.show()
    ↓
RagRepositorySelectionView.show()
    ↓ (displays list, captures input)
User enters selection index
    ↓
View stores selection internally
    ↓
Controller.get_selected_repository() called
    ↓
Controller reads selection from view
    ↓
Controller validates and returns RagRepository
```

### Selection Storage
**Option 1:** View stores selected index
- View has `_selected_index: int | None`
- Controller reads index, maps to repository

**Option 2:** View stores selected repository ID
- View has `_selected_repository_id: str | None`
- Controller reads ID, retrieves full object

**Recommendation:** Option 1 - simpler, view only handles presentation

### Error Handling
- Invalid index → "Invalid selection. Please enter a number between 1 and {count}"
- Corrupted repository → "Repository '{name}' appears corrupted. Skipping."
- No repositories → "No repositories found. Would you like to create one?"

---

## Integration Points

### RagProvider
- `get_repositories()` - returns list of all `rag_*` directories
- Need to add validation: only return repositories with `rag.db`

### RagController
- `select_repository()` - calls selection controller
- `current_rag_repository` - receives selected repository
- `get_rag_state()` - displays repository state after selection

### SessionController
- Provides working directory for repository discovery

---

## Current Implementation Issues

### Issue 1: `get_selected_repository()` Returns None
**Location:** `rag_repository_selection_controller.py:24`
**Problem:** Method doesn't read selection from view
**Fix Required:** 
- View must capture and store user selection
- Controller must read selection from view
- Controller must validate and return repository object

### Issue 2: No Repository Validation
**Problem:** Repositories listed even if corrupted
**Fix Required:**
- Add `validate_repository()` method
- Filter repositories before displaying
- Show warning for invalid repositories

### Issue 3: View Doesn't Capture Selection
**Problem:** View may not store user input
**Fix Required:**
- Verify `RagRepositorySelectionView` captures selection
- Add selection storage if missing
- Provide getter method for controller

---

## Constraints

### Data Integrity
- Only repositories with valid `rag.db` should be selectable
- Corrupted repositories should be reported, not silently ignored
- Empty repositories (no documents) are still valid

### User Experience
- Selection should be immediate (no delay)
- Clear feedback on selection success/failure
- Easy cancellation

### Compatibility
- Repository IDs must match directory names
- Path handling must be cross-platform

---

## Open Questions

1. Should we show repository metadata (creation date, document count) in selection list?
   - **Recommendation:** Not for v1 - add as enhancement

2. Should invalid repositories be removed automatically or just skipped?
   - **Recommendation:** Just skipped - don't delete user data without explicit command

3. Should selection persist across RAG screen sessions?
   - **Recommendation:** Yes - store in `RagController`, clear on explicit deselect

---

*Created: 2026-06-21*
*Status: Analysis Complete - Ready for Design*