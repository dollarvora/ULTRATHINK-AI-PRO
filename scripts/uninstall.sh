#!/bin/bash
#
# ULTRATHINK Uninstall Script
# Removes virtual environment and generated files
#

echo "🎯 ULTRATHINK Uninstall Script"
echo "============================="
echo ""
echo "This will remove:"
echo "- Virtual environment (venv/)"
echo "- Cache files (cache/)"
echo "- Log files (logs/)"
echo "- Preview files (previews/)"
echo ""
echo "This will NOT remove:"
echo "- Configuration files (config/)"
echo "- Output data (output/)"
echo "- Environment file (.env)"
echo ""

read -p "Continue with uninstall? (y/N) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Uninstall cancelled"
    exit 0
fi

echo ""
echo "Removing files..."

# Remove virtual environment
if [ -d "venv" ]; then
    rm -rf venv
    echo "✅ Removed virtual environment"
fi

# Remove cache
if [ -d "cache" ]; then
    find cache -type f ! -name '.gitkeep' -delete
    echo "✅ Cleared cache"
fi

# Remove logs
if [ -d "logs" ]; then
    find logs -type f ! -name '.gitkeep' -delete
    echo "✅ Cleared logs"
fi

# Remove previews
if [ -d "previews" ]; then
    find previews -type f ! -name '.gitkeep' -delete
    echo "✅ Cleared previews"
fi

# Remove Python cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
echo "✅ Removed Python cache"

echo ""
echo "✅ Uninstall complete"
echo ""
echo "To completely remove ULTRATHINK, delete this directory"
echo "To reinstall, run: ./scripts/install.sh"