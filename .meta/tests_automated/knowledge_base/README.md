# Knowledge Base Automated Test Suite

Comprehensive tests for the Meta Harness Knowledge Base system.

## Test Files

- `run_all_tests.sh` - Main test runner script
- `test_kb_functionality.py` - Core functionality tests
- `test_kb_performance.py` - Performance and stress tests
- `test_kb_edge_cases.py` - Edge cases and error handling
- `test_kb_integration.py` - Integration tests
- `test_results.json` - Test results (auto-generated)

## Quick Start

```bash
# Run all tests
./run_all_tests.sh

# Run specific test suite
python test_kb_functionality.py
python test_kb_performance.py
python test_kb_edge_cases.py
python test_kb_integration.py
```

## Test Coverage

### Functionality Tests
- ✅ Search functionality
- ✅ Ask functionality
- ✅ Add entry functionality
- ✅ Stats functionality
- ✅ Explore functionality
- ✅ Population functionality

### Performance Tests
- ⚡ Search speed (< 100ms)
- ⚡ Ask speed (< 200ms)
- ⚡ Batch operations
- ⚡ Memory usage

### Edge Cases
- ⚠️ Empty queries
- ⚠️ Special characters
- ⚠️ Very long queries
- ⚠️ Unicode content
- ⚠️ SQL injection attempts

### Integration Tests
- 🔗 CLI commands
- 🔗 Python API
- 🔗 Database operations
- 🔗 File operations

## Output

Tests generate:
- Console output with colors
- JSON results file
- HTML report (optional)
- Log file
