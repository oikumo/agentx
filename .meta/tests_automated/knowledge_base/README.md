# Knowledge Base Automated Test Suite

Comprehensive tests for the Meta Harness Knowledge Base system.

## Test Files

- `run_all_tests.sh` - Shell wrapper for test runner
- `run_tests.py` - Main Python test runner
- `test_kb_functionality.py` - Core functionality tests (12 tests)
- `test_kb_performance.py` - Performance and stress tests (8 tests)
- `test_kb_edge_cases.py` - Edge cases and error handling (14 tests)
- `test_kb_integration.py` - Integration tests (11 tests)
- `test_kb_populate.py` - Population functionality tests (11 tests)
- `test_results.json` - Test results (auto-generated)
- `TEST_SUMMARY.md` - Comprehensive test documentation

## Quick Start

```bash
# Run all tests
./run_all_tests.sh

# Or using Python
python3 run_tests.py

# Run specific test suite
python3 test_kb_functionality.py
python3 test_kb_performance.py
python3 test_kb_edge_cases.py
python3 test_kb_integration.py
python3 test_kb_populate.py

# Verbose output
python3 run_tests.py --verbose
```

## Test Coverage

### Functionality Tests (12 tests)
- ✅ Search functionality
- ✅ Ask functionality  
- ✅ Add entry functionality
- ✅ Stats functionality
- ✅ Explore functionality
- ✅ Advanced RAG features
- ✅ Query expansion
- ✅ Multi-hop retrieval

### Performance Tests (8 tests)
- ⚡ Search speed (< 100ms) - Actual: ~6ms
- ⚡ Ask speed (< 200ms) - Actual: ~7ms
- ⚡ Batch operations
- ⚡ Memory usage (< 50MB)
- ⚡ Concurrent operations
- ⚡ Database connection reuse

### Edge Cases (14 tests)
- ⚠️ Empty queries
- ⚠️ Special characters
- ⚠️ Very long queries
- ⚠️ Unicode content
- ⚠️ SQL injection attempts
- ⚠️ Invalid inputs
- ⚠️ Boundary conditions

### Integration Tests (11 tests)
- 🔗 CLI commands
- 🔗 Python API
- 🔗 Database operations
- 🔗 End-to-end workflows
- 🔗 Multi-user simulation

### Populate Tests (11 tests)
- 📥 Module import
- 📥 Populator initialization
- 📥 File discovery (META.md, source code)
- 📥 Markdown analysis
- 📥 Python source analysis
- 📥 Entry creation
- 📥 Entry addition
- 📥 Script execution
- 📥 Stats validation

## Output

Tests generate:
- Console output with colors
- JSON results file
- HTML report (optional)
- Log file
