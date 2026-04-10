#!/bin/bash

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

BASE_URL="http://localhost:8000"
COOKIES_FILE="/tmp/auth_cookies.txt"

echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Testing Authentication & CRUD Operations                ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Test 1: Login
echo -e "${YELLOW}Test 1: Login with correct credentials${NC}"
LOGIN_RESPONSE=$(curl -s -c "$COOKIES_FILE" -X POST "$BASE_URL/login/" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}')

if echo "$LOGIN_RESPONSE" | grep -q '"success": true'; then
    echo -e "${GREEN}✓ Login successful${NC}"
    echo "  Response: $LOGIN_RESPONSE"
else
    echo -e "${RED}✗ Login failed${NC}"
    echo "  Response: $LOGIN_RESPONSE"
    exit 1
fi

echo ""

# Test 2: Get CSRF Token
echo -e "${YELLOW}Test 2: Get CSRF token from page${NC}"
CSRF_TOKEN=$(curl -s -b "$COOKIES_FILE" "$BASE_URL/" | grep -oP 'name="csrfmiddlewaretoken" value="\K[^"]+')

if [ -z "$CSRF_TOKEN" ]; then
    echo -e "${RED}✗ Could not get CSRF token${NC}"
    CSRF_TOKEN="dummy"  # Continue with dummy for testing
else
    echo -e "${GREEN}✓ CSRF token obtained${NC}"
    echo "  Token: ${CSRF_TOKEN:0:20}..."
fi

echo ""

# Test 3: Add Company (Authenticated)
echo -e "${YELLOW}Test 3: Add new company (authenticated)${NC}"
ADD_RESPONSE=$(curl -s -b "$COOKIES_FILE" -X POST "$BASE_URL/api/companies/add/" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -d '{
    "name": "Test Tech Ltd",
    "sector": "Technology",
    "logo_url": "https://example.com/logo.png",
    "headquarters": "Dhaka",
    "founded": 2020,
    "description": "Test company for demo"
  }')

if echo "$ADD_RESPONSE" | grep -q '"success": true'; then
    echo -e "${GREEN}✓ Company added successfully${NC}"
    COMPANY_ID=$(echo "$ADD_RESPONSE" | python3 -m json.tool 2>/dev/null | grep '"id"' | head -1 | grep -oE '[0-9]+' | tail -1)
    echo "  Company ID: $COMPANY_ID"
else
    echo -e "${RED}✗ Failed to add company${NC}"
    echo "  Response: $ADD_RESPONSE"
fi

echo ""

# Test 4: Get Companies List
echo -e "${YELLOW}Test 4: Get all companies${NC}"
COMPANIES=$(curl -s "$BASE_URL/api/companies/" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('companies', [])))")

if [ ! -z "$COMPANIES" ] && [ "$COMPANIES" -gt 0 ]; then
    echo -e "${GREEN}✓ Retrieved companies list${NC}"
    echo "  Total companies: $COMPANIES"
else
    echo -e "${RED}✗ Failed to get companies${NC}"
fi

echo ""

# Test 5: Test Unauthorized Access to Add (without auth)
echo -e "${YELLOW}Test 5: Attempt add without authentication${NC}"
UNAUTH_RESPONSE=$(curl -s -X POST "$BASE_URL/api/companies/add/" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","sector":"Tech","headquarters":"Dhaka","founded":2024}' \
  -w "\n%{http_code}")

HTTP_CODE=$(echo "$UNAUTH_RESPONSE" | tail -1)

if [ "$HTTP_CODE" = "403" ] || [ "$HTTP_CODE" = "401" ] || [ "$HTTP_CODE" = "302" ]; then
    echo -e "${GREEN}✓ Unauthorized access blocked (HTTP $HTTP_CODE)${NC}"
else
    echo -e "${YELLOW}⚠ Unexpected response code: $HTTP_CODE${NC}"
fi

echo ""

# Test 6: Logout
echo -e "${YELLOW}Test 6: Logout${NC}"
LOGOUT_RESPONSE=$(curl -s -b "$COOKIES_FILE" -X POST "$BASE_URL/logout/" \
  -H "X-CSRFToken: $CSRF_TOKEN")

if echo "$LOGOUT_RESPONSE" | grep -q '"success": true'; then
    echo -e "${GREEN}✓ Logout successful${NC}"
else
    echo -e "${YELLOW}⚠ Logout response: $LOGOUT_RESPONSE${NC}"
fi

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ All authentication and CRUD tests completed!${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"

# Cleanup
rm -f "$COOKIES_FILE"
