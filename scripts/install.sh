#!/bin/bash
#
# ULTRATHINK Installation Script
# Quick setup for new deployments
#

set -e

echo "🎯 ULTRATHINK Installation Script"
echo "================================"
echo ""

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.11"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Error: Python $REQUIRED_VERSION or higher is required (found $PYTHON_VERSION)"
    exit 1
fi
echo "✅ Python $PYTHON_VERSION found"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists"
else
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Install Playwright browsers
echo ""
echo "Installing Playwright browsers..."
playwright install chromium
playwright install-deps

# Run setup script
echo ""
echo "Running setup..."
python scripts/setup.py

# Create .env file if not exists
if [ ! -f ".env" ]; then
    echo ""
    echo "Creating .env file..."
    cp config/.env.example .env
    echo "✅ .env file created from example"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file with your API keys before running!"
fi

# Validate installation
echo ""
echo "Validating installation..."
python manage.py validate || true

echo ""
echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Update config/employees.csv with your team"
echo "3. Run: source venv/bin/activate"
echo "4. Run: python manage.py validate"
echo "5. Test: python run.py --test --once"
echo ""
echo "For more information, see README.md"