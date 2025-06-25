#!/bin/bash

# ULTRATHINK Enhanced - Repository Cleanup Script
# This script removes development files and makes the repository production-ready

echo "🧹 ULTRATHINK Enhanced - Repository Cleanup"
echo "=========================================="
echo

# Create backup list of files being removed
echo "📋 Creating backup list of removed files..."
BACKUP_LIST="cleanup_backup_list_$(date +%Y%m%d_%H%M%S).txt"

# Files and directories to remove
FILES_TO_REMOVE=(
    # Test files
    "test_*.py"
    "tests/"
    "test_data/"
    
    # Development scripts
    "run_enhanced.sh"
    "run_fresh_data.py"
    "run_full_test.py"
    "run_live_data.py"
    "run_real_gpt.py"
    "send_gpt_preview.py"
    "send_simple_email.py"
    "send_test_email.py"
    
    # Old/backup files
    "create_enhanced_preview.py"
    "create_real_system_enhanced_restored.py"
    "ultrathink_enhanced_complete.py"
    
    # Development documentation
    "CHANGELOG.md"
    "ENHANCED_FEATURES.md"
    "ENHANCEMENTS.md"
    
    # Development tools
    "pytest.ini"
    "pyproject.toml"
    
    # Scripts folder (development utilities)
    "scripts/"
    
    # Output directories (will be recreated as needed)
    "output/"
    "previews/"
    "logs/"
    
    # Virtual environment (shouldn't be in repo)
    "venv/"
    
    # Development requirements
    "requirements.txt"
    "requirements_enhanced.txt"
    
    # Template file
    "gpt_preview_template.html"
    
    # Development configuration
    "manage.py"
    "cli.py"
)

echo "🗑️  Removing development and test files..."

# Remove files and log what's being removed
for item in "${FILES_TO_REMOVE[@]}"; do
    if [ -e "$item" ] || [ -d "$item" ]; then
        echo "Removing: $item" >> "$BACKUP_LIST"
        rm -rf "$item"
        echo "   ✓ Removed: $item"
    fi
done

# Remove specific test files using glob patterns
echo "🧪 Removing test files..."
find . -name "test_*.py" -type f | while read file; do
    echo "Removing: $file" >> "$BACKUP_LIST"
    rm "$file"
    echo "   ✓ Removed: $file"
done

# Clean up cache but keep directories for gitkeep
echo "🗄️  Cleaning cache directories..."
if [ -d "cache" ]; then
    find cache/ -type f -name "*.json" -o -name "*.txt" -o -name "*.log" | while read file; do
        echo "Removing: $file" >> "$BACKUP_LIST"
        rm "$file"
        echo "   ✓ Cleaned: $file"
    done
fi

# Create essential directories with .gitkeep files
echo "📁 Creating essential directories..."
mkdir -p output logs cache
touch output/.gitkeep logs/.gitkeep cache/.gitkeep

echo
echo "✅ Cleanup completed!"
echo "📄 Backup list saved to: $BACKUP_LIST"
echo
echo "🎯 Production-ready files remaining:"
echo "   ✓ create_real_system.py (main application)"
echo "   ✓ run_system.sh (execution script)"
echo "   ✓ requirements_minimal.txt (dependencies)"
echo "   ✓ config/ (configuration)"
echo "   ✓ fetchers/ (data collection)"
echo "   ✓ summarizer/ (AI analysis)"
echo "   ✓ utils/ (core utilities)"
echo "   ✓ emailer/ (report delivery)"
echo "   ✓ README.md (documentation)"
echo "   ✓ .env.example (configuration template)"
echo "   ✓ .gitignore (repository exclusions)"
echo
echo "🚀 Repository is now production-ready!"
echo "   Next steps:"
echo "   1. Copy .env.example to .env and configure your API keys"
echo "   2. Update config/employees.csv with your team"
echo "   3. Run ./run_system.sh to test the system"
echo