#!/bin/bash

# Phase 9 Testing - Enhanced Search, Pagination, Sorting, and Statistics
# This script tests all the new Phase 9 features

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

BASE_URL="http://localhost:8000"
PASSED=0
FAILED=0

# Helper function to run tests
test_endpoint() {
    local description=$1
    local endpoint=$2
    local expected_key=$3
    
    echo -e "\n${BLUE}Testing: ${YELLOW}${description}${NC}"
    echo "Endpoint: ${endpoint}"
    
    response=$(curl -s "${BASE_URL}${endpoint}")
    
    if echo "$response" | grep -q "\"${expected_key}\""; then
        echo -e "${GREEN}✓ PASSED${NC}"
        ((PASSED++))
        echo "Response preview: $(echo $response | head -c 100)..."
    else
        echo -e "${RED}✗ FAILED${NC}"
        echo "Expected key '${expected_key}' not found"
        echo "Response: $response"
        ((FAILED++))
    fi
}

# Welcome message
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Phase 9 Testing - Search, Pagination, Stats             ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"

# ===== Basic API Tests =====
echo -e "\n${BLUE}═════ BASIC API TESTS ═════${NC}"

test_endpoint "Get all companies" "/api/companies/" "companies"
test_endpoint "Get companies stats" "/api/stats/" "total_companies"

# ===== Pagination Tests =====
echo -e "\n${BLUE}═════ PAGINATION TESTS ═════${NC}"

test_endpoint "Pagination page 1 limit 5" "/api/companies/?page=1&limit=5" "pagination"

echo -e "\n${BLUE}Testing: ${YELLOW}Verify pagination metadata${NC}"
response=$(curl -s "${BASE_URL}/api/companies/?page=1&limit=3")
if echo "$response" | grep -q '"pages": 5'; then
    echo -e "${GREEN}✓ PASSED${NC} - Correct page count (13 companies, 3 per page = 5 pages)"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC} - Page count incorrect"
    ((FAILED++))
fi

echo -e "\n${BLUE}Testing: ${YELLOW}Pagination page 2${NC}"
response=$(curl -s "${BASE_URL}/api/companies/?page=2&limit=5")
if echo "$response" | grep -q '"page": 2'; then
    echo -e "${GREEN}✓ PASSED${NC} - Returns page 2"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC} - Page 2 not working"
    ((FAILED++))
fi

# ===== Search Tests =====
echo -e "\n${BLUE}═════ SEARCH TESTS ═════${NC}"

echo -e "\n${BLUE}Testing: ${YELLOW}Search for 'Bank'${NC}"
response=$(curl -s "${BASE_URL}/api/companies/?search=Bank")
if echo "$response" | grep -q '"total": 3'; then
    echo -e "${GREEN}✓ PASSED${NC} - Found 3 companies with 'Bank'"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC} - Search didn't return expected results"
    ((FAILED++))
fi

echo -e "\n${BLUE}Testing: ${YELLOW}Search for 'Dhaka'${NC}"
response=$(curl -s "${BASE_URL}/api/companies/?search=Dhaka")
if echo "$response" | grep -q '"total"'; then
    total=$(echo "$response" | grep -o '"total": [0-9]*' | grep -o '[0-9]*')
    if [ "$total" -gt 0 ]; then
        echo -e "${GREEN}✓ PASSED${NC} - Found $total companies with 'Dhaka'"
        ((PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - No results for 'Dhaka'"
        ((FAILED++))
    fi
fi

# ===== Sector Filter Tests =====
echo -e "\n${BLUE}═════ SECTOR FILTER TESTS ═════${NC}"

echo -e "\n${BLUE}Testing: ${YELLOW}Filter by Telecom sector${NC}"
response=$(curl -s "${BASE_URL}/api/companies/?sector=Telecom")
if echo "$response" | grep -q '"total": 3'; then
    echo -e "${GREEN}✓ PASSED${NC} - Found 3 Telecom companies"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC} - Sector filter not working"
    ((FAILED++))
fi

echo -e "\n${BLUE}Testing: ${YELLOW}Filter by Technology sector${NC}"
response=$(curl -s "${BASE_URL}/api/companies/?sector=Technology")
if echo "$response" | grep -q '"total": 1'; then
    echo -e "${GREEN}✓ PASSED${NC} - Found 1 Technology company"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC} - Technology filter not working"
    ((FAILED++))
fi

# ===== Combined Filter Tests =====
echo -e "\n${BLUE}═════ COMBINED FILTER + PAGINATION TESTS ═════${NC}"

echo -e "\n${BLUE}Testing: ${YELLOW}Sector filter with pagination${NC}"
response=$(curl -s "${BASE_URL}/api/companies/?sector=Telecom&page=1&limit=2")
if echo "$response" | grep -q '"pages": 2'; then
    echo -e "${GREEN}✓ PASSED${NC} - Telecom companies paginated correctly (3 items, 2 per page = 2 pages)"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC} - Combined sector filter and pagination not working"
    ((FAILED++))
fi

echo -e "\n${BLUE}Testing: ${YELLOW}Search with pagination${NC}"
response=$(curl -s "${BASE_URL}/api/companies/?search=Bank&page=1&limit=10")
if echo "$response" | grep -q '"pages": 1'; then
    echo -e "${GREEN}✓ PASSED${NC} - Bank search with pagination working (3 results fit in 1 page)"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC} - Search with pagination not working"
    ((FAILED++))
fi

# ===== Statistics Tests =====
echo -e "\n${BLUE}═════ STATISTICS TESTS ═════${NC}"

echo -e "\n${BLUE}Testing: ${YELLOW}Stats endpoint returns total_companies${NC}"
response=$(curl -s "${BASE_URL}/api/stats/")
if echo "$response" | grep -q '"total_companies": 13'; then
    echo -e "${GREEN}✓ PASSED${NC} - Total companies count is 13"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC} - Stats total not correct"
    ((FAILED++))
fi

echo -e "\n${BLUE}Testing: ${YELLOW}Stats endpoint returns sector breakdown${NC}"
response=$(curl -s "${BASE_URL}/api/stats/")
if echo "$response" | grep -q '"sectors"'; then
    sector_count=$(echo "$response" | grep -o '"count"' | wc -l)
    echo -e "${GREEN}✓ PASSED${NC} - Sector breakdown returned ($sector_count sectors)"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC} - Sector breakdown not found"
    ((FAILED++))
fi

echo -e "\n${BLUE}Testing: ${YELLOW}Stats endpoint returns all_sectors list${NC}"
response=$(curl -s "${BASE_URL}/api/stats/")
if echo "$response" | grep -q '"all_sectors"'; then
    echo -e "${GREEN}✓ PASSED${NC} - All sectors list returned"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC} - All sectors list not found"
    ((FAILED++))
fi

# ===== Summary =====
echo -e "\n${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Phase 9 Test Summary                                   ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"

echo -e "\n${GREEN}✓ Passed: $PASSED${NC}"
echo -e "${RED}✗ Failed: $FAILED${NC}"

if [ $FAILED -eq 0 ]; then
    echo -e "\n${GREEN}All Phase 9 tests passed! 🎉${NC}"
    exit 0
else
    echo -e "\n${RED}Some tests failed. Please review.${NC}"
    exit 1
fi
