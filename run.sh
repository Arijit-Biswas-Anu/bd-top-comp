#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$SCRIPT_DIR"
VENV_DIR="$SCRIPT_DIR/../venv"

echo -e "${BLUE}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   🚀 BD Top Companies - Django Development Server    ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}❌ Virtual environment not found at: $VENV_DIR${NC}"
    echo -e "${YELLOW}   Please create it first:${NC}"
    echo -e "${YELLOW}   cd $PROJECT_DIR && python3 -m venv ../venv${NC}"
    exit 1
fi

# Kill any existing process on port 8000
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${YELLOW}⚠ Port 8000 already in use. Cleaning up...${NC}"
    lsof -ti:8000 | xargs kill -9 2>/dev/null
    sleep 1
fi

# Activate virtual environment
echo -e "${GREEN}✓ Activating virtual environment...${NC}"
source "$VENV_DIR/bin/activate"

# Check if Django is installed
if ! python -c "import django" 2>/dev/null; then
    echo -e "${YELLOW}❌ Django not found. Installing dependencies...${NC}"
    pip install django==6.0.4 -q
fi

# Navigate to project directory
cd "$PROJECT_DIR"

# Run migrations if needed
echo -e "${GREEN}✓ Running migrations...${NC}"
python manage.py migrate --run-syncdb -q 2>/dev/null

# Display server info
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📱 Server Information:${NC}"
echo -e "${BLUE}   URL: ${GREEN}http://localhost:8000${NC}"
echo -e "${BLUE}   Admin: ${GREEN}http://localhost:8000/admin${NC}"
echo -e "${BLUE}   Credentials: ${YELLOW}admin${NC} / ${YELLOW}admin123${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo ""

# Start server
python manage.py runserver 0.0.0.0:8000
