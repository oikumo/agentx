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
- `test_opencode_integration.py` - OpenCode agent integration tests (20 tests)
- `test_opencode_commands.py` - OpenCode command integration tests (15 tests)
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
python3 test_opencode_integration.py
python3 test_opencode_commands.py

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

### OpenCode Integration Tests (20 tests)
- 🤖 Agent startup workflow
- 🤖 KB-first rule enforcement
- 🤖 Context switching
- 🤖 Query patterns (where, how, what, when, why)
- 🤖 Multi-hop reasoning
- 🤖 Query expansion
- 🤖 Context persistence
- 🤖 Concurrent access
- 🤖 Session state management
- 🤖 Mistake handling
- 🤖 Invalid input handling
- 🤖 Error recovery
- 🤖 Query latency (< 1s)
- 🤖 Batch operations
- 🤖 Memory efficiency
- 🤖 RAG augmentation
- 🤖 Confidence scoring
- 🤖 Category filtering
- 🤖 Entry creation
- 🤖 Knowledge evolution

### OpenCode Command Tests (15 tests)
- 🖥️ CLI commands (search, ask, stats, add, explore, correct)
- 🖥️ Python API (search, ask, stats, add_entry)
- 🖥️ Agent startup sequence
- 🖥️ KB-first workflow
- 🖥️ Task completion workflow
- 🖥️ Meta commands

## Output

Tests generate:
- Console output with colors
- JSON results file
- HTML report (optional)
- Log file
