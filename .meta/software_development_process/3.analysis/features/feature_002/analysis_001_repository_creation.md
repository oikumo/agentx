# ANALYSIS: RAG Repository Creation

## Use Case: Create New RAG Repository

### Primary Actor
- User

### Preconditions
- User is in RAG main menu
- Session has valid working directory for RAG
- User has selected "Create Repository" option

### Main Flow
1. User selects "Create Repository" from RAG main menu
2. System displays repository creation screen
3. System prompts user for repository name
4. User enters repository name (without prefix)
5. System validates name:
   - Not empty
   - No special characters (alphanumeric + underscore only)
   - Does not already exist in working directory
6. System creates directory: `{working_directory}/rag_{repository_name}/`
7. System initializes SQLite database (`rag.db`) with ingestion tracking table
8. System displays success message with repository path
9. System returns to repository selection screen with new repository listed

### Alternative Flows

#### A1: Invalid Repository Name
- 5a. System detects invalid name format
- 5b. System displays error message
- 5c. Return to step 3

#### A2: Repository Already Exists
- 5a. System detects existing directory with same name
- 5b. System displays error: "Repository '{name}' already exists"
- 5c. Return to step 3

#### A3: User Cancels
- 3a. User enters empty name or cancel command
- 3b. System displays "Repository creation cancelled"
- 3c. Return to RAG main menu

### Postconditions
- New repository directory created with `rag_` prefix
- SQLite database initialized with proper schema
- Repository appears in repository selection list
- No repository is automatically selected (user must explicitly select)

---

## Domain Concepts

### New Classes Required
None - existing classes sufficient:
- `RagRepository` (dataclass) - represents repository
- `RagProvider` - can discover new repository
- `RagDatabase` - initializes database schema

### Existing Classes to Extend
- `RagCreateRepositoryController` - currently empty, needs implementation
- `RagCreateRepositoryView` - needs creation

---

## UI Requirements

### Input Screen
- Prompt: "Enter repository name (without 'rag_' prefix):"
- Validation feedback for invalid names
- Success confirmation with full path

### Navigation
- Entry: From RAG main menu → "Create Repository"
- Exit: Return to repository selection screen or main menu

---

## Operations Extracted

### 1. `create_repository(name: str) -> bool`
**Location:** `RagCreateRepositoryController`
**Purpose:** Create new repository directory and initialize database

**Preconditions:**
- Name is non-empty string
- Name contains only alphanumeric characters and underscores
- Directory does not already exist

**Exceptions:**
- Invalid name format → return False with error message
- Directory creation fails → return False with error message
- Database initialization fails → return False with error message

**Postconditions:**
- Directory exists at `{working_directory}/rag_{name}/`
- `rag.db` exists with proper schema
- Returns True on success

### 2. `validate_repository_name(name: str) -> tuple[bool, str]`
**Location:** `RagCreateRepositoryController`
**Purpose:** Validate repository name format and availability

**Preconditions:**
- Name is string (may be empty)

**Exceptions:**
- None - validation handles all cases

**Postconditions:**
- Returns (True, "") if valid
- Returns (False, error_message) if invalid

### 3. `initialize_repository_directory(name: str) -> Path | None`
**Location:** `RagCreateRepositoryController`
**Purpose:** Create directory structure

**Preconditions:**
- Name is validated
- Working directory is accessible

**Exceptions:**
- Permission denied → return None
- Path traversal detected → return None

**Postconditions:**
- Directory created if successful
- Returns Path to new directory or None

### 4. `initialize_database(directory: Path) -> bool`
**Location:** `RagCreateRepositoryController` or reuse `RagDatabase`
**Purpose:** Create SQLite database with ingestion tracking table

**Preconditions:**
- Directory exists
- Directory is writable

**Exceptions:**
- Database creation fails → return False

**Postconditions:**
- `rag.db` exists in directory
- Table `ingestion` exists with proper schema
- Returns True on success

---

## UI Behavior Specification

### Screen Flow
```
RAG Main Menu
    ↓ (user selects "Create Repository")
Repository Creation Screen
    ↓ (user enters name)
Validation
    ↓ (valid)
Directory Creation → DB Initialization → Success Message
    ↓
Repository Selection Screen (shows new repository)
```

### Input Validation Rules
1. **Empty check:** Name must not be empty or whitespace-only
2. **Format check:** Only alphanumeric and underscore allowed
3. **Prefix check:** Name must not start with "rag_" (system adds automatically)
4. **Existence check:** Directory must not already exist
5. **Length check:** Name length between 1-50 characters

### Error Messages
- "Repository name cannot be empty"
- "Repository name contains invalid characters (use letters, numbers, underscore only)"
- "Repository name must not include 'rag_' prefix (added automatically)"
- "Repository '{name}' already exists"
- "Repository name too long (max 50 characters)"
- "Failed to create repository directory"
- "Failed to initialize database"

---

## Integration Points

### Session Controller
- `SessionController.get_directory_rag()` - provides working directory

### RagProvider
- Auto-discovers new repository on next `get_repositories()` call

### RagDatabase
- Can reuse initialization logic from existing `RagDatabase` class

---

## Constraints

### Security
- Prevent path traversal attacks (reject names with "..", "/", "\")
- Validate against shell injection patterns

### Usability
- Clear error messages
- Minimal steps to create repository
- Immediate feedback on success/failure

### Compatibility
- Repository name becomes directory name → filesystem-safe characters only
- Cross-platform path handling (use `pathlib.Path`)

---

## Open Questions

1. Should repository creation automatically select the new repository?
   - **Recommendation:** No - user should explicitly select to avoid confusion

2. Should we allow repository description/metadata at creation time?
   - **Recommendation:** No - keep minimal for v1, add later as enhancement

3. What happens if database initialization fails after directory creation?
   - **Recommendation:** Clean up directory, report error, allow retry

---

*Created: 2026-06-21*
*Status: Analysis Complete - Ready for Design*