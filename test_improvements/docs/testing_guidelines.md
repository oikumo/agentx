# Testing Guidelines for Agent-X

This document outlines the testing standards and best practices for the Agent-X project.

## Test Organization

### Directory Structure
```
tests/
├── unit/                   # Unit tests (fast, isolated)
│   ├── utils/              # Utility function tests
│   ├── models/             # Model/data structure tests
│   ├── api/                # API component tests
│   ├── cli/                # CLI interface tests
│   └── core/               # Core application logic tests
├── integration/            # Integration tests (cross-component)
│   ├── api_integration/    # API service integration tests
│   ├── agent_interactions/ # Agent-to-agent communication tests
│   └── end_to_end/         # End-to-end workflow tests
├── e2e/                    # End-to-end tests (full system)
│   ├── cli_workflows/      # CLI user interaction tests
│   ├── api_workflows/      # API user interaction tests
│   └── user_journeys/      # Complete user journey tests
└── performance/            # Performance and load tests
```

### Test Naming Conventions
1. **Test Files**: `[component]_test.py` (e.g., `utils_test.py`, `api_client_test.py`)
2. **Test Classes**: `[Component]Test` (e.g., `UtilsTest`, `APIClientTest`)
3. **Test Methods**: `test_[scenario]_[expected_behavior]` (e.g., `test_valid_input_returns_correct_output`)
4. **Parametrized Tests**: Use descriptive IDs for parameters

### Test Structure Guidelines

#### 1. Arrange-Act-Assert Pattern
```python
def test_example_function():
    # Arrange - Set up preconditions and inputs
    test_input = "test_value"
    expected_result = "expected_output"

    # Act - Execute the function or behavior under test
    actual_result = function_under_test(test_input)

    # Assert - Verify the expected outcome
    assert actual_result == expected_result
```

#### 2. Exception Testing
```python
def test_exception_handling():
    # Arrange
    invalid_input = None

    # Act & Assert
    with pytest.raises(ValueError, match="Input cannot be None"):
        function_under_test(invalid_input)
```

#### 3. Parameterized Tests
```python
@pytest.mark.parametrize("input_value,expected_output", [
    ("valid_input", "expected_result"),
    ("edge_case", "edge_result"),
    pytest.param("invalid_input", None, marks=pytest.mark.xfail)
])
def test_with_parameters(input_value, expected_output):
    assert function_under_test(input_value) == expected_output
```

#### 4. Fixture Usage
```python
@pytest.fixture
def sample_data():
    return {"key": "value"}

def test_using_fixture(sample_data):
    assert sample_data["key"] == "value"
```

## Quality Standards

### 1. Coverage Requirements
- **Minimum**: 80% line coverage for new code
- **Target**: 90%+ line coverage for critical components
- **Critical Path**: 95%+ coverage for authentication, data validation, and core business logic

### 2. Test Independence
- Each test must be able to run independently
- No shared mutable state between tests
- Use fixtures for shared setup/teardown

### 3. Mocking Guidelines
- Mock external dependencies (APIs, databases, file system)
- Do not mock internal functions unless testing isolation
- Use `unittest.mock` or `pytest-mock` for mocking
- Verify mocks were called as expected when relevant

### 4. Performance Considerations
- Unit tests should complete in < 100ms
- Integration tests should complete in < 1s
- Avoid expensive operations in tests when possible
- Use `@pytest.mark.slow` for tests that exceed time limits

## Specific Component Guidelines

### API Clients
1. Test all HTTP methods (GET, POST, PUT, DELETE, PATCH)
2. Test error status codes (4xx, 5xx)
3. Test timeout and retry behavior
4. Test authentication header handling
5. Test request/response serialization/deserialization
6. Test rate limiting and backoff strategies

### Utility Functions
1. Test edge cases (empty inputs, None values, boundary conditions)
2. Test type validation and conversion
3. Test error conditions and exception raising
4. Test performance characteristics for algorithms

### Core Application Logic
1. Test state transitions and state machine behavior
2. Test error recovery and fallback mechanisms
3. Test concurrent access patterns
4. Test resource cleanup and disposal

### CLI Interface
1. Test command parsing and argument validation
2. Test help text and version output
3. Test error message formatting
4. Test exit codes for success/failure scenarios
5. Test subcommand execution and chaining

### Configuration Management
1. Test loading from environment variables
2. Test default value application
3. Test validation of required fields
4. Test type conversion and coercion
5. Test sensitive data handling (no logging of secrets)

## Test Data Strategies

### 1. Factory Pattern
Use factory functions or classes to generate test data:
```python
class MessageFactory:
    @staticmethod
    def create_user_message(content):
        return {"role": "user", "content": content}

    @staticmethod
    def create_assistant_message(content):
        return {"role": "assistant", "content": content}
```

### 2. Fixtures for Common Objects
```python
@pytest.fixture
def sample_config():
    return Config(api_key="test", model="gpt-3.5-turbo")
```

### 3. Test Data Libraries
Consider using libraries like:
- `factory-boy` for object creation
- `faker` for realistic test data
- `hypothesis` for property-based testing

## Continuous Integration

### Test Execution in CI
1. Run unit tests on every commit
2. Run integration tests on pull requests
3. Run performance tests nightly
4. Generate coverage reports for every build

### Test Reporting
1. Use pytest-html for rich test reports
2. Generate JUnit XML for CI integration
3. Track coverage trends over time
4. Flaky test detection and quarantine

## Common Pitfalls to Avoid

### 1. Over-Mocking
- Don't mock too much - test real integration when possible
- Mock only external dependencies and I/O operations

### 2. Brittle Tests
- Avoid testing implementation details
- Focus on behavior and outcomes
- Use meaningful assertions, not exact string matches when inappropriate

### 3. Slow Tests
- Avoid file I/O, network calls, or sleeps in unit tests
- Use in-memory databases or mock services
- Mark slow tests appropriately

### 4. Test Pollution
- Clean up after each test (files, database state, global variables)
- Use fixture teardown or context managers
- Reset singletons and global state

## Property-Based Testing (Advanced)

Consider using `hypothesis` for property-based testing:
```python
from hypothesis import given, strategies as st

@given(st.text(min_size=1))
def test_message_processing_never_crashes(text):
    # Should not raise for any non-empty string
    result = process_message(text)
    assert isinstance(result, str)
```

## Security Testing Guidelines

### 1. Input Validation
- Test SQL injection attempts
- Test XSS payload attempts
- Test path traversal attempts
- Test command injection attempts

### 2. Authentication & Authorization
- Test unauthorized access attempts
- Test token validation and expiration
- Test privilege escalation attempts

### 3. Data Protection
- Test that secrets are not logged
- Test encryption of sensitive data at rest
- Test secure transmission of sensitive data

## Legacy Test Migration

When migrating existing tests:
1. Maintain test behavior - don't change what is being tested
2. Improve test structure and readability
3. Add missing test cases for edge cases
4. Remove duplicate or redundant tests
5. Update to use new fixtures and patterns

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Mocking with unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
- [Hypothesis for property-based testing](https://hypothesis.works/)
- [Factory Boy for test fixtures](https://factoryboy.readthedocs.io/)

## Questions and Support

For questions about testing practices:
1. Check existing test files for examples
2. Consult the testing chapter in CONTRIBUTING.md
3. Ask in the #testing channel on Slack
4. Review test-related issues in the GitHub repository