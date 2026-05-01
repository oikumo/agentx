# AgentX Unit Tests

Comprehensive unit test suite for the AgentX project, covering all core modules with isolated tests.

## Test Results

**Total Tests**: 205  
**Status**: ✅ All Passing  
**Coverage**: Core modules (common, model, controllers, views, db)

## Test Organization

Tests are organized by module structure mirroring `src/agentx/`:

```.
tests/unit/
├── common/                      # Common utilities
│   ├── test_utils.py           # safe_int, clear_console, directory ops, StreamingMetrics
│   └── test_security.py        # Security constants
├── model/                       # Data models
│   ├── session/                 # Session management
│   │   ├── test_adaptive_petri_net.py      # Petri net implementation
│   │   ├── test_session.py                 # Session class
│   │   ├── test_session_manager.py         # SessionManager singleton
│   │   ├── test_session_state_manager.py   # State management
│   │   └── test_petri_net_visualizer.py    # ASCII visualization
│   └── db/                      # Database layer
│       └── test_session_db.py  # Database schemas and operations
├── controllers/                 # Controller layer
│   └── main_controller/         # Main controller
│       ├── test_commands_base.py           # Command base classes
│       ├── test_commands_parser.py         # Command parsing
│       ├── test_commands.py                # All command implementations
│       └── test_main_controller.py         # MainController (TODO)
└── views/                       # View layer
    ├── common/
    │   └── test_console.py     # Console logging
    └── main_view/
        └── test_main_view.py   # MainView UI
```

## Running Tests

```bash
# Run all tests
uv run pytest tests/unit/ -v

# Run specific test file
uv run pytest tests/unit/common/test_utils.py -v

# Run specific test class
uv run pytest tests/unit/model/session/test_adaptive_petri_net.py::TestPlace -v

# Run with coverage (if pytest-cov installed)
uv run pytest tests/unit/ --cov=agentx --cov-report=html
```

## Test Categories

### 1. Common Utilities (`common/`)
- **safe_int**: Integer conversion with error handling
- **clear_console**: Cross-platform console clearing
- **Directory operations**: Create, check existence, delete
- **StreamingMetrics**: Token and time tracking for streaming responses
- **Security constants**: Allowed directories, session defaults

### 2. Model Layer (`model/`)
#### Petri Net Implementation
- **Place**: Token storage and management
- **Transition**: Firing logic, input/output arcs
- **AdaptivePetriNet**: Net construction, state management
- **SessionState**: State representation

#### Session Management
- **Session**: Creation, naming, directory management
- **SessionDatabase**: SQLite operations, history tracking
- **SessionManager**: Singleton pattern, session lifecycle
- **SessionStateManager**: State machine with Petri nets
- **PetriNetVisualizer**: ASCII art visualization

### 3. Controllers (`controllers/`)
#### Command Pattern
- **CommandResult**: Abstract base for command results
- **Command**: Abstract base with key and description
- **CommandParser**: Text parsing into CommandData
- **Command implementations**:
  - QuitCommand, ClearCommand
  - HistoryCommand, HelpCommand
  - SumCommand, AIChat
  - NewCommand (session management)
  - PetriNetStatusCommand, PetriNetPrintCommand
  - GoalCommand (session objectives)

### 4. Views (`views/`)
- **Console**: Logging with ANSI colors (info, success, error, warning)
- **MainView**: User interface, input capture, response display

### 5. Database (`db/`)
- **TableHistory**: History table schema and operations
- **TableUser**: User table schema
- **HistoryEntry/History**: Data structures

## Test Patterns Used

### Mocking
- Extensive use of `unittest.mock.MagicMock` and `patch`
- Isolates tests from external dependencies (filesystem, database, LLM APIs)
- Example:
```python
@patch('agentx.common.utils.Path')
def test_create_directory(self, mock_path):
    mock_path.return_value = MagicMock()
    # Test logic here
```

### Data Classes
- Testing dataclass creation and field access
- Verifying default values and field types

### Abstract Classes
- Testing that abstract base classes cannot be instantiated
- Verifying concrete implementations satisfy contracts

### Singleton Pattern
- Testing singleton behavior in SessionManager
- Proper cleanup with `setup_method`

## Key Test Coverage

### Petri Net Tests (45+ tests)
- Place creation and token management
- Transition firing and arc connections
- Net construction and state tracking
- Session state extraction
- ASCII visualization

### Command Tests (60+ tests)
- All command types (Quit, Clear, History, Help, Sum, AIChat, New, etc.)
- Command parsing and argument handling
- Result application (logging, printing)
- Error handling

### Session Management Tests (40+ tests)
- Session creation with/without timestamps
- Database operations (history tracking)
- Session lifecycle (create, backup, delete)
- Singleton pattern enforcement

### Utility Tests (30+ tests)
- Integer conversion edge cases
- Directory operations (create, check, delete)
- Console operations across platforms
- Metrics tracking (tokens, time)

## Excluded from Tests

The following modules were NOT tested in this batch:
- **Services/AI modules**: Require API keys and external services
- **MainController integration**: Requires full system setup
- **LLM-based generators**: Require API configuration

These can be added as integration tests in `tests/integration/`.

## Quality Metrics

- ✅ All 205 tests passing
- ✅ No production code modified
- ✅ Isolated unit tests (no external dependencies)
- ✅ Comprehensive mocking of side effects
- ✅ Clear test organization matching source structure

## Future Improvements

1. **Add integration tests** for end-to-end workflows
2. **Add coverage reporting** to track percentage
3. **Add property-based tests** for Petri net operations
4. **Add performance tests** for large session histories
5. **Create test fixtures** for common test data

## Notes

- All tests are isolated and don't modify production code
- Filesystem operations are mocked to prevent actual disk writes
- Database operations use in-memory mocks
- No external API calls (LLM, vector stores) in unit tests
