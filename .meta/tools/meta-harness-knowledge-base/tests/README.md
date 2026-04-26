# Knowledge Base Testing

This directory contains comprehensive tests for the Meta Harness Knowledge Base tool.

## Test Files

1. `test_knowledge_base.py` - Tests for the knowledge base entry point
2. `test_rag_tool.py` - Tests for the RAG tool functionality
3. `test_script.py` - A simple test script to verify functionality
4. `README.md` - This file

## Test Coverage

The tests cover all major functionality of the knowledge base:

- Adding knowledge base entries
- Searching for entries
- Asking questions with RAG
- Correcting existing entries
- Running evolution cycles
- Getting statistics

## Running Tests

To run the tests, use the following command from the project root:

```bash
uv run pytest tests/ -v
```

## Test Approach

The tests use an in-memory SQLite database for testing to ensure isolation and speed. Each test creates its own database instance with the required schema.

For integration testing, the `test_script.py` file provides a simple way to verify the knowledge base functionality end-to-end.