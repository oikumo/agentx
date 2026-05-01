#!/bin/bash
# Run Goal Command Tests

echo "========================================"
echo "Running Goal Command Tests"
echo "========================================"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"

# Run the Python test script
echo "Running stdio tests..."
cd "$PROJECT_ROOT"
uv run python3 "$SCRIPT_DIR/test_goal_stdio.py"

# Capture exit code
EXIT_CODE=$?

echo ""
echo "========================================"
if [ $EXIT_CODE -eq 0 ]; then
    echo "✓ All tests passed!"
else
    echo "✗ Some tests failed"
fi
echo "========================================"

exit $EXIT_CODE
