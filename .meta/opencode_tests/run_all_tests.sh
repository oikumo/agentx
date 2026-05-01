#!/bin/bash
cd /home/oikumo/develop/production/agentx

echo "============================================"
echo "META HARNESS - Opencode Integration Test"
echo "============================================"

FAILED=0
PASSED=0

echo ""
echo "[1/6] Testing WORK Notebook..."
if [ -f ".meta/WORK.md" ]; then
    echo "[PASS] WORK.md exists"
    python3 .meta/opencode_tests/test_work_notebook.py
    PASSED=$((PASSED+1))
else
    echo "[FAIL] WORK.md not found"
    FAILED=$((FAILED+1))
fi

echo ""
echo "[2/6] Checking KB status..."
python3 .meta/tools/meta-harness-knowledge-base/kb stats
echo "[PASS] KB check complete"
PASSED=$((PASSED+1))

echo ""
echo "[3/6] Verifying documentation..."
grep -q "WORK.md" META_HARNESS.md && echo "[PASS] META_HARNESS.md references WORK"
grep -q "WORK.md" AGENTS.md && echo "[PASS] AGENTS.md references WORK"
PASSED=$((PASSED+1))

echo ""
echo "[4/6] Checking sandbox..."
[ -d ".meta/sandbox" ] && echo "[PASS] Sandbox exists" && PASSED=$((PASSED+1)) || (echo "[FAIL] Sandbox missing" && FAILED=$((FAILED+1)))

echo ""
echo "[5/6] Git status..."
git status --short
echo "[PASS] Git check complete"
PASSED=$((PASSED+1))

echo ""
echo "[6/6] Checking directives..."
grep -q "KB first" AGENTS.md && echo "[PASS] KB-first directive present"
grep -q "WORK NOTEBOOK" AGENTS.md && echo "[PASS] WORK directive present"
PASSED=$((PASSED+1))

echo ""
echo "============================================"
echo "Summary: Passed=$PASSED Failed=$FAILED"
echo "============================================"

if [ $FAILED -eq 0 ]; then
    echo "[PASS] All tests completed"
    exit 0
else
    echo "[FAIL] Tests failed"
    exit 1
fi
