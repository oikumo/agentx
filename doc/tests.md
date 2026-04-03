# Tests - Agent-X

**Path**: `/tests/`

Unit tests using `unittest` framework.

---

## Module Structure

```
tests/
├── integration/
│   └── __init__.py
└── unit/
    ├── app/
    │   └── __init__.py
    └── applications/
        └── repl_app/
            └── command_line_controller/
                ├── command_parser_test.py
                └── commands_controller_test.py
```

---

## Command Parser Tests

### tests/unit/applications/repl_app/command_line_controller/command_parser_test.py

**Classes**:
- `CommandDataTest(unittest.TestCase)` - tests for `CommandData` dataclass:
  - `test_creation_stores_key_and_arguments`
  - `test_empty_arguments_list_is_valid`
  - `test_equality_is_value_based`
  - `test_inequality_on_different_key`
- `CommandParserTest(unittest.TestCase)` - tests for `CommandParser`:
  - `test_add_appends_command_to_list`
  - `test_add_multiple_commands`
  - `test_parse_single_word_returns_command_data`
  - `test_parse_command_with_arguments`
  - `test_parse_command_with_single_argument`
  - `test_parse_empty_string_returns_none_and_warns`
  - `test_parse_whitespace_only_returns_none_and_warns`
  - `test_parse_extra_whitespace_between_tokens_is_normalised`

---

## Commands Controller Tests

### tests/unit/applications/repl_app/command_line_controller/commands_controller_test.py

**Class**: `CommandsControllerTest(unittest.TestCase)`

Tests for command registration and lookup:
- `test_empty_on_init`
- `test_add_command_makes_it_findable`
- `test_add_multiple_commands`
- `test_find_command_returns_none_for_unknown_key`
- `test_get_commands_returns_all_registered_commands`

**Note**: Tests reference `CommandsController` which maps to `MainController` in the current codebase.

---

## Test Commands

```bash
# Run all tests
pytest

# Run unit tests only
pytest tests/unit -q

# Run integration tests only
pytest tests/integration -q

# Run specific test
pytest tests/path/to/test_file.py::TestClass::test_function_name -q

# Run tests matching pattern
pytest tests/path/to/test_file.py -k "pattern" -q
```
