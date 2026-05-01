#!/bin/bash
# Petri Net Session State Management - Test Runner
# This script runs all Petri Net integration tests using uv

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}AgentX Petri Net Session State - Test Suite${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""
echo -e "${YELLOW}Project Root:${NC} $PROJECT_ROOT"
echo -e "${YELLOW}Test Directory:${NC} $SCRIPT_DIR"
echo ""

# Change to project root
cd "$PROJECT_ROOT"

# Test 1: Integration Tests
echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}TEST 1: Petri Net Integration Tests${NC}"
echo -e "${BLUE}============================================================${NC}"
uv run python test_automated/session_management_petri_nets/test_petri_integration.py
echo ""

# Test 2: E2E Tests
echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}TEST 2: AgentX with Petri Net E2E Tests${NC}"
echo -e "${BLUE}============================================================${NC}"
uv run python test_automated/session_management_petri_nets/test_agentx_with_petri.py
echo ""

# Test 3: Feature Tests
echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}TEST 3: Petri Net Features Tests${NC}"
echo -e "${BLUE}============================================================${NC}"
uv run python test_automated/session_management_petri_nets/test_petri_net_features.py
echo ""

# Summary
echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}ALL TESTS COMPLETED${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""
echo -e "${GREEN}✓ All test scripts executed successfully${NC}"
echo ""
